from backend.orchestrator.multiscale_intelligence import (
    build_multiscale_intelligence
)


def validate_multiscale(
    zone
):

    zone = build_multiscale_intelligence(
        zone
    )

    return zone