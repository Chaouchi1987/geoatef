from fastapi import APIRouter, Request
from backend.core.config import settings
from backend.core.auth import current_user
from backend.gee.auth import earth_engine_status

router=APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status":"ok","service":settings.app_name,"version":settings.app_version}

@router.get("/health/earth-engine")
def ee_health(request:Request):
    try:
        user=current_user(request)
    except Exception:
        return {"status":"login_required","project":settings.earth_engine_project}
    return earth_engine_status(user["sub"])
