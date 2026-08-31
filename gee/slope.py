import ee

from backend.gee.ee_init import (
    init_ee
)


def get_slope(
    lat,
    lon
):

    init_ee()

    point = ee.Geometry.Point(
        [lon, lat]
    )

    dem = ee.Image(
        "USGS/SRTMGL1_003"
    )

    slope = ee.Terrain.slope(
        dem
    )

    stats = slope.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point.buffer(30),
        scale=30,
        maxPixels=1e9
    )

    result = stats.getInfo()

    print(
        "SLOPE RESULT =",
        result
    )

    return result["slope"]