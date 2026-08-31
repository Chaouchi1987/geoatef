from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class AOIRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_m: float = Field(gt=0, le=500)
    scale_m: int = Field(default=10, description="Requested investigation/sample scale in meters")
    geometry_type: str = Field(default="circle", pattern=r"^(circle|square)$")

class AOIResponse(BaseModel):
    aoi_id: str
    latitude: float
    longitude: float
    radius_m: float
    scale_m: int
    area_m2: float
    bbox: list[float]

class AnalysisStartRequest(BaseModel):
    aoi_id: str
    scale_m: int = Field(default=10, ge=10, le=500)
    start_date: str = "2024-01-01"
    end_date: str = "2026-01-01"
    cloud_pct: float = Field(default=20, ge=0, le=100)

class Target(BaseModel):
    target_id: str
    latitude: float
    longitude: float
    box_geojson: dict[str, Any]
    anomaly_score: float
    zscore_score: float
    isolation_forest_score: float
    geological_score: float
    evidence: list[str]
    data_quality: dict[str, Any]

class AnalysisStatus(BaseModel):
    analysis_id: str
    status: str
    stage: str
    message: str | None = None
    error: str | None = None
    progress: float | None = None
