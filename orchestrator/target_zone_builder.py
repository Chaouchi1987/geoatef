from backend.contracts.target_zone import (
    TargetZone
)


def build_target_zone(
    cluster
):

    zone = TargetZone(

        center_lat=
            cluster["lat"],

        center_lon=
            cluster["lon"],

        diameter_m=
            cluster["diameter_m"],

        cells=
            cluster["cells"],

        mean_score=
            cluster["mean_score"],

        max_score=
            cluster["max_score"]

    )

    zone.confidence = (
        cluster["mean_score"]
    )

    zone.zone_points = (
        cluster["points"]
    )

    if zone.mean_score >= 80:

        zone.category = (
            "High Priority"
        )

    elif zone.mean_score >= 60:

        zone.category = (
            "Medium Priority"
        )

    else:

        zone.category = (
            "Low Priority"
        )

    return zone