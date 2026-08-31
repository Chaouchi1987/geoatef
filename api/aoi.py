from fastapi import APIRouter, Request
from backend.models.schemas import AOIRequest, AOIResponse
from backend.processing.grid import make_aoi_bbox
from backend.processing.aoi import circle_geojson, square_geojson
from backend.core.auth import current_user
from backend.core.store import AOIS
import uuid, math

router = APIRouter(prefix="/aoi", tags=["aoi"])

@router.post("", response_model=AOIResponse)
def create_aoi(req: AOIRequest, request: Request):
    user=current_user(request)
    bbox = make_aoi_bbox(req.latitude, req.longitude, req.radius_m)
    area = (math.pi * req.radius_m**2) if req.geometry_type == "circle" else (4 * req.radius_m**2)
    aoi_id = str(uuid.uuid4())
    AOIS[aoi_id] = {
        "aoi_id": aoi_id,
        "user_id": user["sub"],
        "latitude": req.latitude,
        "longitude": req.longitude,
        "radius_m": req.radius_m,
        "scale_m": req.scale_m,
        "bbox": bbox,
        "geometry_type": req.geometry_type,
        "geometry": circle_geojson(req.latitude, req.longitude, req.radius_m) if req.geometry_type == "circle" else square_geojson(req.latitude, req.longitude, req.radius_m),
    }
    return AOIResponse(
        aoi_id=aoi_id,
        latitude=req.latitude,
        longitude=req.longitude,
        radius_m=req.radius_m,
        scale_m=req.scale_m,
        area_m2=area,
        bbox=bbox,
    )
