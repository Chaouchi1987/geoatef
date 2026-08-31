from backend.gee.ndvi import get_ndvi
from backend.gee.ndwi import get_ndwi
from backend.gee.ndbi import get_ndbi

from backend.gee.dem import get_elevation
from backend.gee.slope import get_slope

from backend.gee.iron_oxide import get_iron_oxide
from backend.gee.clay_ratio import get_clay_ratio


def extract_features(cell, radius=50):

    lat = cell["lat"]
    lon = cell["lon"]

    try:

        return {

            "lat": lat,
            "lon": lon,

            "ndvi": get_ndvi(lat, lon, radius),

            "ndwi": get_ndwi(lat, lon, radius),

            "ndbi": get_ndbi(lat, lon, radius),

            "elevation": get_elevation(lat, lon),

            "slope": get_slope(lat, lon),

            "iron": get_iron_oxide(lat, lon, radius),

            "clay": get_clay_ratio(lat, lon, radius)

        }

    except Exception as e:

        print("FEATURE ERROR:", e)

        return None