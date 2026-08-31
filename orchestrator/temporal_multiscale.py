from backend.gee.temporal_features_buffer import (
    get_yearly_features_buffer
)

from backend.fusion.temporal_stability_engine import (
    build_temporal_stability
)


def run_temporal_multiscale(

    lat,
    lon

):

    radii = [

        50,

        100,

        200

    ]

    results = {}

    scores = []

    for radius in radii:

        yearly = (

            get_yearly_features_buffer(

                lat=lat,

                lon=lon,

                start_year=2018,

                end_year=2025,

                radius_m=radius

            )

        )

        stability = (

            build_temporal_stability(
                yearly
            )

        )

        score = stability[
            "temporal_score"
        ]

        results[
            f"{radius}m"
        ] = score

        scores.append(
            score
        )

    results[
        "mean_temporal"
    ] = round(

        sum(scores)

        /

        len(scores),

        2

    )

    return results