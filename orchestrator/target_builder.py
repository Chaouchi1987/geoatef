from backend.contracts.target_model import (
    Target
)


def build_target(

    lat,
    lon,

    ai_score=0,

    geology_score=0,

    temporal_score=0,

    thermal_score=0,

    structural_score=0

):

    target = Target(

        lat=lat,

        lon=lon
    )

    target.ai_score = ai_score

    target.geology_score = geology_score

    target.temporal_score = temporal_score

    target.thermal_score = thermal_score

    target.structural_score = structural_score

    return target