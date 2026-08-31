import ee

from backend.gee.ee_init import (
    init_ee
)

from backend.gee.aster_sampler import (
    get_aster_period
)


def get_aster_features(
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

    ferric_iron = (

        image.select("B02")

        .divide(

            image.select("B01")

        )

        .rename("ferric_iron")

    )

    clay_index = (

        image.select("B05")

        .divide(

            image.select("B06")

        )

        .rename("clay_index")

    )

    values = (

        ferric_iron

        .addBands(
            clay_index
        )

        .reduceRegion(

            reducer=ee.Reducer.mean(),

            geometry=point,

            scale=30,

            maxPixels=1e9

        )
    )

    info = values.getInfo()

    return {

        "ferric_iron":
            info.get(
                "ferric_iron"
            ),

        "clay_index":
            info.get(
                "clay_index"
            )

    }