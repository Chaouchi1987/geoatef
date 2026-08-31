from __future__ import annotations

import ee

from backend.gee.ee_init import init_ee


def build_dem_features(geometry: ee.Geometry) -> ee.Image:
    """
    Build real terrain features from the SRTM DEM in Google Earth Engine.

    Returned bands:
      elevation : metres
      slope     : degrees
      aspect    : degrees

    The function deliberately returns an ee.Image and does not call getInfo(),
    so the features remain server-side until the final sampling step.
    """
    init_ee()

    dem = ee.Image("USGS/SRTMGL1_003").select("elevation").rename("elevation")

    terrain = ee.Terrain.products(dem)

    slope = terrain.select("slope").rename("slope")
    aspect = terrain.select("aspect").rename("aspect")

    return dem.addBands([slope, aspect])


def get_elevation(lat: float, lon: float):
    """Backward-compatible point elevation helper for legacy/report code."""
    init_ee()
    point = ee.Geometry.Point([float(lon), float(lat)])
    dem = ee.Image("USGS/SRTMGL1_003").select("elevation")
    result = dem.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point.buffer(30),
        scale=30,
        maxPixels=1e9,
    ).getInfo()
    if "elevation" not in result or result["elevation"] is None:
        raise RuntimeError("No SRTM elevation value was returned for the requested point.")
    return float(result["elevation"])
    