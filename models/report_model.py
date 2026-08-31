from pydantic import BaseModel


class ReportModel(BaseModel):

    latitude: float
    longitude: float
    radius_m: float

    ndvi: float
    ndwi: float

    elevation_m: float
    slope_deg: float

    ndbi: float
    iron_oxide: float
    clay_ratio: float