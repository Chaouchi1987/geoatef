from __future__ import annotations
import hashlib, hmac, os, sqlite3, time
from pathlib import Path
import jwt
from fastapi import HTTPException, Request

DB = Path(__file__).resolve().parents[2] / "data" / "geoanomaly.db"
DB.parent.mkdir(parents=True, exist_ok=True)
SECRET = os.getenv("GEOANOMALY_SECRET")
if not SECRET:
    # Development-only fallback; production deployments must provide a secret.
    SECRET = hashlib.sha256(os.urandom(32)).hexdigest()

LOCAL_EE_MARKER = "__LOCAL_DEVICE_EE__"

def db():
    conn=sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at REAL NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS ee_connections(
        user_id INTEGER PRIMARY KEY,
        refresh_token TEXT NOT NULL,
        updated_at REAL NOT NULL,
        mode TEXT NOT NULL DEFAULT 'oauth'
    )""")
    # Migrate databases created by earlier GeoAnomaly versions.
    cols={row[1] for row in conn.execute("PRAGMA table_info(ee_connections)").fetchall()}
    if "mode" not in cols:
        conn.execute("ALTER TABLE ee_connections ADD COLUMN mode TEXT NOT NULL DEFAULT 'oauth'")
    conn.commit()
    return conn

def hash_password(password: str) -> str:
    salt=os.urandom(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,240000)
    return salt.hex()+":"+digest.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex,digest_hex=stored.split(":")
        digest=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),240000)
        return hmac.compare_digest(digest.hex(),digest_hex)
    except Exception:
        return False

def create_token(user_id:int,username:str):
    return jwt.encode({"sub":str(user_id),"username":username,"exp":int(time.time())+86400},SECRET,algorithm="HS256")

def current_user(request:Request):
    auth=request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        raise HTTPException(401,"Authentication required.")
    try:
        return jwt.decode(auth[7:],SECRET,algorithms=["HS256"])
    except Exception:
        raise HTTPException(401,"Invalid or expired session.")

def ee_connection(user_id:str):
    conn=db()
    try:
        row=conn.execute("SELECT refresh_token,mode,updated_at FROM ee_connections WHERE user_id=?",(int(user_id),)).fetchone()
        if not row: return None
        return {"refresh_token":row[0],"mode":row[1],"updated_at":row[2]}
    finally: conn.close()

def ee_connected(user_id:str)->bool:
    return ee_connection(user_id) is not None
