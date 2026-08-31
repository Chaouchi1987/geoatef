import ee

from backend.gee.ee_init import (
    init_ee
)


def get_aster_period(
    start_date,
    end_date
):

    init_ee()

    image = (

        ee.ImageCollection(
            "ASTER/AST_L1T_003"
        )

        .filterDate(
            start_date,
            end_date
        )

        .median()

    )

    return image