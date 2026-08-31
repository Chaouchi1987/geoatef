from backend.gee.ndvi import get_ndvi
from backend.gee.ndwi import get_ndwi
from backend.gee.dem import get_elevation
from backend.gee.slope import get_slope
from backend.gee.ndbi import get_ndbi
from backend.gee.iron_oxide import get_iron_oxide
from backend.gee.clay_ratio import get_clay_ratio

from backend.models.report_model import ReportModel


def build_report(lat, lon, radius):

    return ReportModel(

        latitude=lat,
        longitude=lon,
        radius_m=radius,

        ndvi=get_ndvi(lat, lon, radius),
        ndwi=get_ndwi(lat, lon, radius),

        elevation_m=get_elevation(lat, lon),
        slope_deg=get_slope(lat, lon),

        ndbi=get_ndbi(lat, lon, radius),
        iron_oxide=get_iron_oxide(lat, lon, radius),
        clay_ratio=get_clay_ratio(lat, lon, radius)
    )