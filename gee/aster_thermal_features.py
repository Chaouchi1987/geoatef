import ee

from backend.gee.ee_init import (
    init_ee
)

from backend.gee.aster_sampler import (
    get_aster_period
)


def get_aster_thermal_features(
    lat,
    lon,
    start_date,
    end_date
):

    init_ee()

    point = ee.Geometry.Point(
        [lon, lat]
    )

    image = get_aster_period(
        start_date,
        end_date
    )

    thermal = (

        image.select(
            [
                "B10",
                "B11",
                "B12",
                "B13",
                "B14"
            ]
        )

        .reduceRegion(

            reducer=ee.Reducer.mean(),

            geometry=point,

            scale=90,

            maxPixels=1e9

        )
    )

    info = thermal.getInfo()

    return {

        "B10":
            info.get("B10"),

        "B11":
            info.get("B11"),

        "B12":
            info.get("B12"),

        "B13":
            info.get("B13"),

        "B14":
            info.get("B14")

    }