from __future__ import annotations

import os
from backend.core.config import settings
from backend.core.auth import db, ee_connection, LOCAL_EE_MARKER

_initialized = False
_last_error = None
_current_user = None


def _local_initialize() -> bool:
    """Initialize Earth Engine from the developer machine's persistent credentials."""
    import ee
    ee.Initialize(project=settings.earth_engine_project)
    # Real API request: initialization alone is not considered connected.
    ee.Number(1).getInfo()
    return True


def _oauth_initialize(refresh_token: str) -> bool:
    """Initialize EE with this user's Google OAuth refresh token."""
    if not settings.google_oauth_client_id or not settings.google_oauth_client_secret:
        raise RuntimeError(
            "Production Google OAuth is not configured. "
            "Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET."
        )

    import ee
    from google.oauth2.credentials import Credentials

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret,
        scopes=["https://www.googleapis.com/auth/earthengine.readonly"],
    )

    # google-auth refreshes the access token only when an actual request needs it.
    ee.Initialize(
        credentials=credentials,
        project=settings.earth_engine_project,
    )
    ee.Number(1).getInfo()
    return True


def initialize_for_user(user_id: str) -> bool:
    global _initialized, _last_error, _current_user

    conn = db()
    try:
        row = conn.execute(
            "SELECT refresh_token,mode FROM ee_connections WHERE user_id=?",
            (int(user_id),),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        _initialized = False
        _last_error = "This user has not connected Google Earth Engine."
        return False

    try:
        mode = row[1]
        if mode == "local" or row[0] == LOCAL_EE_MARKER:
            if not settings.allow_local_ee_auth:
                raise RuntimeError("Local Earth Engine authentication is disabled.")
            _local_initialize()
        else:
            _oauth_initialize(row[0])

        _initialized = True
        _last_error = None
        _current_user = str(user_id)
        return True

    except Exception as exc:
        _initialized = False
        _last_error = str(exc)
        return False


def earth_engine_status(user_id: str | None = None) -> dict:
    if user_id is None:
        return {
            "status": "login_required",
            "project": settings.earth_engine_project,
            "user_scoped": True,
        }

    conn = ee_connection(user_id)
    if conn:
        ok = initialize_for_user(user_id)
        if ok:
            return {
                "status": "ready",
                "connected": True,
                "mode": conn["mode"],
                "project": settings.earth_engine_project,
                "user_scoped": True,
            }

        message = _last_error or "Earth Engine authorization failed."
        return {
            "status": "error",
            "connected": False,
            "mode": conn["mode"],
            "project": settings.earth_engine_project,
            "message": message,
            "user_scoped": True,
        }

    return {
        "status": "authorization_required",
        "connected": False,
        "mode": None,
        "project": settings.earth_engine_project,
        "message": "Earth Engine is not connected for this user.",
        "user_scoped": True,
    }
