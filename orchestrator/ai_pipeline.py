from backend.fusion.intelligence_engine import (
    build_intelligence_score
)


def run_ai_pipeline(

    geology_score,
    thermal_score,
    temporal_score,
    structural_score,
    ai_score,

    multiscale_score=0

):

    result = build_intelligence_score(

        geology_score=geology_score,

        thermal_score=thermal_score,

        temporal_score=temporal_score,

        structural_score=structural_score,

        ai_score=ai_score,

        multiscale_score=multiscale_score

    )

    return result