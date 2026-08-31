"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.orchestrator.target_builder import (
    build_target
)

from backend.fusion.intelligence_engine import (
    build_intelligence_score
)


def run_full_analysis(

    lat,
    lon,

    ai_score,

    geology_score,

    temporal_score,

    thermal_score,

    structural_score

):

    target = build_target(

        lat=lat,

        lon=lon,

        ai_score=ai_score,

        geology_score=geology_score,

        temporal_score=temporal_score,

        thermal_score=thermal_score,

        structural_score=structural_score

    )

    intelligence = (

        build_intelligence_score(

            geology_score=
                target.geology_score,

            thermal_score=
                target.thermal_score,

            temporal_score=
                target.temporal_score,

            structural_score=
                target.structural_score,

            ai_score=
                target.ai_score

        )
    )

    target.intelligence_score = (

        intelligence[
            "intelligence_score"
        ]
    )

    target.category = (

        intelligence[
            "category"
        ]
    )

    target.confidence = (

        intelligence[
            "confidence"
        ]
    )

    target.reasons = (

        intelligence[
            "reasons"
        ]
    )

    return target