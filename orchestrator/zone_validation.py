from backend.orchestrator.zone_intelligence import (
    build_zone_intelligence
)


def validate_zone(
    zone
):

    validated = build_zone_intelligence(
        zone
    )

    return validated


def validate_top_zones(
    zones,
    top_n=3
):

    validated = []

    for zone in zones[:top_n]:

        validated.append(
            validate_zone(
                zone
            )
        )

    return validated