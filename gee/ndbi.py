import ee

from backend.gee.ee_init import (
    init_ee
)


def get_ndbi(
    lat,
    lon,
    radius
):

    init_ee()

    point = ee.Geometry.Point(
        [lon, lat]
    )

    image = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(point)
        .filterDate(
            "2025-01-01",
            "2025-12-31"
        )
        .median()
    )

    ndbi = image.normalizedDifference(
        ["B11", "B8"]
    )

    stats = ndbi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point.buffer(radius),
        scale=10,
        maxPixels=1e9
    )

    result = stats.getInfo()

    print(
        "NDBI RESULT =",
        result
    )

    return result["nd"]