from __future__ import annotations
from contextvars import ContextVar
import threading

_user_id: ContextVar[str | None] = ContextVar("geoanomaly_ee_user", default=None)
_analysis_lock = threading.RLock()

def set_ee_user(user_id: str):
    return _user_id.set(str(user_id))

def reset_ee_user(token):
    _user_id.reset(token)

def init_ee(user_id: str | None = None):
    uid = str(user_id) if user_id is not None else _user_id.get()
    if not uid:
        raise RuntimeError("No authenticated Earth Engine user is bound to this analysis.")
    from backend.gee.auth import initialize_for_user
    if not initialize_for_user(uid):
        from backend.gee.auth import earth_engine_status
        status=earth_engine_status(uid)
        raise RuntimeError(status.get("message") or "Earth Engine authorization failed.")

def analysis_lock():
    return _analysis_lock
