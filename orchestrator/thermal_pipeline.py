"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.gee.thermal_features import (
    get_thermal_value
)

from backend.gee.thermal_annulus import (
    get_annulus_temperature
)

from backend.fusion.thermal_contrast_engine import (
    build_thermal_contrast
)

from backend.fusion.thermal_score_engine import (
    build_thermal_score
)


def run_thermal_pipeline(

    lat,
    lon,

    start_date,
    end_date

):

    target_temp = get_thermal_value(

        lat=lat,

        lon=lon,

        start_date=start_date,

        end_date=end_date

    )

    annulus_temp = (

        get_annulus_temperature(

            lat=lat,

            lon=lon,

            start_date=start_date,

            end_date=end_date

        )

    )

    contrast = (

        build_thermal_contrast(

            target_temp=target_temp,

            neighborhood_temp=annulus_temp

        )

    )

    thermal_score = (

        contrast["contrast_score"]

    )

    return {

        "target_temp":
            target_temp,

        "annulus_temp":
            annulus_temp,

        "contrast":
            contrast["contrast"],

        "thermal_score":
            thermal_score

    }