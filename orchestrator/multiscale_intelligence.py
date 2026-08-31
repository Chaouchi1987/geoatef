from backend.orchestrator.temporal_multiscale import (
    run_temporal_multiscale
)


def build_multiscale_intelligence(
    zone
):

    result = run_temporal_multiscale(

        lat=zone.center_lat,

        lon=zone.center_lon

    )

    scores = [

        result["50m"],

        result["100m"],

        result["200m"]

    ]

    variation = (

        max(scores)

        -

        min(scores)

    )

    spatial_stability = round(

        100 - variation,

        2

    )

    zone.multiscale_score = (
        spatial_stability
    )

    zone.spatial_stability = (
        spatial_stability
    )

    return zone