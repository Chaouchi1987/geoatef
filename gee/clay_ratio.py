import ee

from backend.gee.ee_init import (
    init_ee
)


def get_clay_ratio(
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

    clay = (
        image.select("B11")
        .divide(
            image.select("B12")
        )
        .rename("clay")
    )

    stats = clay.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point.buffer(radius),
        scale=20,
        maxPixels=1e9
    )

    result = stats.getInfo()

    print(
        "CLAY RATIO RESULT =",
        result
    )

    return result["clay"]