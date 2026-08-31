from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field
from backend.auth.store import register, login, current_user
import uuid

router = APIRouter(prefix="/auth", tags=["authentication"])

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register_user(req: RegisterRequest):
    try:
        u = register(str(uuid.uuid4()), req.username, req.email, req.password)
        return {"user_id": u.user_id, "username": u.username, "email": u.email}
    except ValueError as e:
        raise HTTPException(409, str(e))

@router.post("/login")
def login_user(req: LoginRequest):
    try:
        token = login(req.username, req.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(401, str(e))

@router.get("/me")
def me(authorization: str | None = Header(default=None)):
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    user = current_user(token)
    if not user:
        raise HTTPException(401, "Not authenticated.")
    return {"user_id": user.user_id, "username": user.username, "email": user.email}
