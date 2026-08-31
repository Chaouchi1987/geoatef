"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.orchestrator.temporal_pipeline import (
    run_temporal_pipeline
)

from backend.orchestrator.thermal_pipeline import (
    run_thermal_pipeline
)

from backend.orchestrator.ai_pipeline import (
    run_ai_pipeline
)

from backend.orchestrator.structural_pipeline import (
    run_structural_pipeline
)

from backend.cache.temporal_cache import (
    get_cached,
    set_cached
)


def build_zone_intelligence(
    zone
):

    # -------------------------
    # Temporal (Cached)
    # -------------------------

    temporal = get_cached(

        zone.center_lat,

        zone.center_lon

    )

    if temporal is None:

        temporal = run_temporal_pipeline(

            lat=zone.center_lat,

            lon=zone.center_lon

        )

        set_cached(

            zone.center_lat,

            zone.center_lon,

            temporal

        )

    # -------------------------
    # Thermal
    # -------------------------

    thermal = run_thermal_pipeline(

        lat=zone.center_lat,

        lon=zone.center_lon,

        start_date="2025-01-01",

        end_date="2025-12-31"

    )

    # -------------------------
    # Structural
    # -------------------------

    structural = run_structural_pipeline(
        zone.zone_points
    )

    # -------------------------
    # Anthropogenic Risk
    # -------------------------

    anthropogenic_risk = 0

    if zone.diameter_m > 30:
        anthropogenic_risk += 25

    if zone.cells > 10:
        anthropogenic_risk += 20

    if structural.structural_score < 40:
        anthropogenic_risk += 20

    anthropogenic_risk = min(
        anthropogenic_risk,
        100
    )

    # -------------------------
    # Intelligence
    # -------------------------

    result = run_ai_pipeline(

        geology_score=zone.mean_score,

        thermal_score=thermal[
            "thermal_score"
        ],

        temporal_score=temporal[
            "temporal_score"
        ],

        structural_score=
            structural.structural_score,

        # Use the zone's actual statistical anomaly score; never fabricate an AI score.
        ai_score=max(0.0,min(1.0,float(zone.mean_score or 0))),

        multiscale_score=
            zone.multiscale_score

    )

    # -------------------------
    # Penalty
    # -------------------------

    final_intelligence = (

        result["intelligence_score"]

        -

        anthropogenic_risk

    )

    final_intelligence = max(
        final_intelligence,
        0
    )

    # -------------------------
    # Update Zone
    # -------------------------

    zone.temporal_score = (
        temporal["temporal_score"]
    )

    zone.thermal_score = (
        thermal["thermal_score"]
    )

    zone.structural_score = (
        structural.structural_score
    )

    zone.anthropogenic_risk = (
        anthropogenic_risk
    )

    zone.intelligence_score = (
        round(
            final_intelligence,
            2
        )
    )

    zone.category = (
        result["category"]
    )

    zone.reasons = (
        result["reasons"]
    )

    print(
        "ANTHROPOGENIC RISK =",
        anthropogenic_risk
    )

    print(
        "FINAL INTELLIGENCE =",
        zone.intelligence_score
    )

    return zone