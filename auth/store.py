from __future__ import annotations
from dataclasses import dataclass, asdict
from backend.auth.security import hash_password, verify_password, new_session_token

@dataclass
class User:
    user_id: str
    username: str
    email: str
    password_hash: str

USERS: dict[str, User] = {}
SESSIONS: dict[str, str] = {}

def register(user_id: str, username: str, email: str, password: str) -> User:
    if username.lower() in {u.username.lower() for u in USERS.values()}:
        raise ValueError("Username already exists.")
    if email.lower() in {u.email.lower() for u in USERS.values()}:
        raise ValueError("Email already exists.")
    user = User(user_id, username, email, hash_password(password))
    USERS[user_id] = user
    return user

def login(username: str, password: str) -> str:
    user = next((u for u in USERS.values() if u.username.lower() == username.lower()), None)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid username or password.")
    token = new_session_token()
    SESSIONS[token] = user.user_id
    return token

def current_user(token: str | None) -> User | None:
    if not token:
        return None
    uid = SESSIONS.get(token)
    return USERS.get(uid) if uid else None
