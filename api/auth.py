from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from backend.core.auth import db, hash_password, verify_password, create_token, current_user
import re, time

router=APIRouter(prefix="/auth",tags=["auth"])

class Signup(BaseModel):
    email:str
    username:str=Field(min_length=3,max_length=32)
    password:str=Field(min_length=10,max_length=128)

class Login(BaseModel):
    username:str
    password:str

@router.post("/signup")
def signup(body:Signup):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+",body.username):
        raise HTTPException(400,"Username may contain letters, numbers, _, ., and - only.")
    conn=db()
    try:
        cur=conn.execute("INSERT INTO users(username,email,password_hash,created_at) VALUES(?,?,?,?)",
                         (body.username.lower(),body.email.lower(),hash_password(body.password),time.time()))
        conn.commit()
        return {"access_token":create_token(cur.lastrowid,body.username.lower()),"username":body.username.lower()}
    except Exception:
        raise HTTPException(409,"Username or email already exists.")
    finally: conn.close()

@router.post("/login")
def login(body:Login):
    conn=db(); row=conn.execute("SELECT id,username,password_hash FROM users WHERE username=?",
                                (body.username.lower(),)).fetchone()
    conn.close()
    if not row or not verify_password(body.password,row[2]):
        raise HTTPException(401,"Invalid username or password.")
    return {"access_token":create_token(row[0],row[1]),"username":row[1]}

@router.get("/me")
def me(request:Request):
    payload=current_user(request)
    return {"user_id":payload["sub"],"username":payload["username"]}
