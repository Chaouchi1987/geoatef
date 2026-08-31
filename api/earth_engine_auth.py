from __future__ import annotations
import time, secrets, urllib.parse, requests
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from backend.core.auth import current_user, db, ee_connection, ee_connected, LOCAL_EE_MARKER
from backend.core.config import settings
from backend.gee.auth import initialize_for_user

router = APIRouter(prefix="/auth/earth-engine", tags=["earth-engine-oauth"])
GOOGLE_AUTH="https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN="https://oauth2.googleapis.com/token"
SCOPES="openid email profile https://www.googleapis.com/auth/earthengine.readonly"

def config_error():
    if not settings.google_oauth_client_id: return "Google OAuth Client ID is not configured on the server."
    if not settings.google_oauth_client_secret: return "Google OAuth Client Secret is not configured on the server."
    if not settings.google_oauth_redirect_uri: return "Google OAuth Redirect URI is not configured on the server."
    return None

@router.get("/status")
def status(request: Request):
    user=current_user(request)
    s=__import__("backend.gee.auth",fromlist=["earth_engine_status"]).earth_engine_status(user["sub"])
    s["oauth_configured"]=config_error() is None
    s["local_dev_available"]=bool(settings.allow_local_ee_auth)
    return s



@router.get("/diagnostic/network")
def network_diagnostic(request: Request):
    """Safe connectivity diagnostics; never returns credentials or tokens."""
    import socket
    result = {
        "oauth_host": "oauth2.googleapis.com",
        "dns": None,
        "tcp": None,
    }
    try:
        addresses = socket.getaddrinfo("oauth2.googleapis.com", 443, type=socket.SOCK_STREAM)
        result["dns"] = sorted({a[4][0] for a in addresses})
        sock = socket.create_connection(("oauth2.googleapis.com", 443), timeout=5)
        sock.close()
        result["tcp"] = "ok"
    except Exception as exc:
        result["error"] = str(exc)
    return result

@router.get("/diagnostic")
def diagnostic(request: Request):
    """Developer diagnostic: tests the actual Earth Engine API without changing user state."""
    if not settings.allow_local_ee_auth:
        raise HTTPException(403, "Local Earth Engine authentication is disabled.")
    try:
        import ee
        ee.Initialize(project=settings.earth_engine_project)
        value = ee.Number(1).getInfo()
        return {
            "ok": True,
            "project": settings.earth_engine_project,
            "ee_request": value,
            "mode": "local",
        }
    except Exception as exc:
        return {
            "ok": False,
            "project": settings.earth_engine_project,
            "mode": "local",
            "error": str(exc),
            "action": "Run `earthengine authenticate` once on this computer, then retry.",
        }

@router.post("/local-connect")
def local_connect(request: Request):
    if not settings.allow_local_ee_auth:
        raise HTTPException(403,"Local Earth Engine authentication is disabled.")
    user=current_user(request)
    try:
        import ee
        ee.Initialize(project=settings.earth_engine_project)
        ee.Number(1).getInfo()
    except Exception as exc:
        detail = str(exc)
        if "oauth2.googleapis.com" in detail or "NameResolutionError" in detail or "ConnectionError" in detail:
            message = (
                "Earth Engine credentials were found, but Google OAuth token refresh failed. "
                "This is a network/TLS/authentication problem, not an AOI or analysis problem. "
                "Retry after connectivity is restored. Details: " + detail
            )
        else:
            message = (
                "Local Earth Engine credentials are not usable on this computer. "
                "Run `python -c \"import ee; ee.Authenticate()\"` inside the project's .venv, then retry. "
                "Details: " + detail
            )
        raise HTTPException(503, message)
    conn=db()
    try:
        conn.execute("INSERT OR REPLACE INTO ee_connections(user_id,refresh_token,updated_at,mode) VALUES(?,?,?,?)",(int(user["sub"]),LOCAL_EE_MARKER,time.time(),"local"))
        conn.commit()
    finally: conn.close()
    return {"connected":True,"mode":"local","project":settings.earth_engine_project,"message":"Earth Engine is connected using this computer's local developer credentials. This mode is for local testing only."}

@router.get("/start")
def start(request: Request):
    user=current_user(request)
    error=config_error()
    if error:
        raise HTTPException(503,error+" For local testing you can use /auth/earth-engine/local-connect instead.")
    state=secrets.token_urlsafe(32)
    conn=db()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS oauth_states(state TEXT PRIMARY KEY,user_id INTEGER,expires REAL)")
        conn.execute("INSERT INTO oauth_states(state,user_id,expires) VALUES(?,?,?)",(state,int(user["sub"]),time.time()+600))
        conn.commit()
    finally: conn.close()
    params={"client_id":settings.google_oauth_client_id,"redirect_uri":settings.google_oauth_redirect_uri,"response_type":"code","scope":SCOPES,"access_type":"offline","prompt":"consent","include_granted_scopes":"true","state":state}
    return {"authorization_url":GOOGLE_AUTH+"?"+urllib.parse.urlencode(params)}

@router.get("/callback")
def callback(code:str,state:str):
    if config_error(): raise HTTPException(503,"Google OAuth server configuration is incomplete.")
    conn=db(); row=conn.execute("SELECT user_id,expires FROM oauth_states WHERE state=?",(state,)).fetchone()
    if not row or row[1] < time.time(): conn.close(); raise HTTPException(400,"Invalid or expired OAuth state.")
    user_id=int(row[0])
    try:
        r=requests.post(GOOGLE_TOKEN,data={"code":code,"client_id":settings.google_oauth_client_id,"client_secret":settings.google_oauth_client_secret,"redirect_uri":settings.google_oauth_redirect_uri,"grant_type":"authorization_code"},timeout=20)
        r.raise_for_status(); token=r.json(); refresh=token.get("refresh_token")
        if not refresh: raise RuntimeError("Google did not return a refresh token. Re-authorize with consent.")
        conn.execute("INSERT OR REPLACE INTO ee_connections(user_id,refresh_token,updated_at,mode) VALUES(?,?,?,?)",(user_id,refresh,time.time(),"oauth"))
        conn.execute("DELETE FROM oauth_states WHERE state=?",(state,)); conn.commit()
        return RedirectResponse(url=settings.frontend_after_ee_callback)
    except requests.HTTPError as exc:
        conn.rollback(); detail=exc.response.text[:500] if exc.response is not None else str(exc); raise HTTPException(502,"Google OAuth token exchange failed: "+detail)
    except Exception as exc:
        conn.rollback(); raise HTTPException(502,"Google OAuth exchange failed: "+str(exc))
    finally: conn.close()
