from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.health import router as health_router
from backend.api.aoi import router as aoi_router
from backend.api.analysis import router as analysis_router
from backend.api.auth import router as auth_router
from backend.api.earth_engine_auth import router as ee_auth_router
from backend.api.report import router as report_router

app=FastAPI(title=settings.app_name,version=settings.app_version,
            description="Scientific geospatial anomaly analysis platform.")

origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins or ["*"],allow_credentials=True,
                   allow_methods=["*"],allow_headers=["*"])

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(ee_auth_router)
app.include_router(aoi_router)
app.include_router(analysis_router)
app.include_router(report_router)

@app.get("/")
def root():
    return {"service":settings.app_name,"status":"running"}
