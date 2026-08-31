"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.orchestrator.analysis_context import (
    AnalysisContext
)

from backend.orchestrator.feature_pipeline import (
    run_feature_pipeline
)

from backend.orchestrator.geology_pipeline import (
    run_geology_pipeline
)

from backend.orchestrator.temporal_pipeline import (
    run_temporal_pipeline
)

from backend.orchestrator.thermal_pipeline import (
    run_thermal_pipeline
)

from backend.orchestrator.ai_pipeline import (
    run_ai_pipeline
)

from backend.contracts.target_model import (
    Target
)


def run_full_analysis_v4(

    cells,

    lat,
    lon,

    start_date="2025-01-01",

    end_date="2025-12-31"

):

    context = AnalysisContext()

    # ---------------------------------
    # Feature Pipeline
    # ---------------------------------

    context.df = run_feature_pipeline(

        cells=cells,

        start_date=start_date,

        end_date=end_date

    )

    # ---------------------------------
    # Geology Pipeline
    # ---------------------------------

    context.geology = run_geology_pipeline(
        context.df
    )

    geology_score = float(

        context.geology.iloc[0][
            "geology_score"
        ]

    )

    # ---------------------------------
    # Temporal Pipeline
    # ---------------------------------

    context.temporal = run_temporal_pipeline(

        lat=lat,

        lon=lon

    )

    temporal_score = (

        context.temporal[
            "temporal_score"
        ]

    )

    # ---------------------------------
    # Thermal Pipeline
    # ---------------------------------

    context.thermal = run_thermal_pipeline(

        lat=lat,

        lon=lon,

        start_date=start_date,

        end_date=end_date

    )

    thermal_score = (

        context.thermal[
            "thermal_score"
        ]

    )

    # ---------------------------------
    # AI Pipeline
    # ---------------------------------

    context.ai = run_ai_pipeline(

        geology_score=
            geology_score,

        thermal_score=
            thermal_score,

        temporal_score=
            temporal_score,

        structural_score=0,

        # Deprecated engine: use only an explicitly supplied statistical score.
        # A fixed 100/1.0 value is scientifically invalid.
        ai_score=float(getattr(context, "ai_score", 0.0) or 0.0)

    )

    # ---------------------------------
    # Target
    # ---------------------------------

    target = Target(

        lat=lat,

        lon=lon

    )

    target.ai_score = float(getattr(context, "ai_score", 0.0) or 0.0)

    target.geology_score = geology_score

    target.temporal_score = temporal_score

    target.thermal_score = thermal_score

    target.structural_score = 0

    target.intelligence_score = (

        context.ai[
            "intelligence_score"
        ]

    )

    target.category = (

        context.ai[
            "category"
        ]

    )

    target.confidence = (

        context.ai[
            "confidence"
        ]

    )

    target.reasons = (

        context.ai[
            "reasons"
        ]

    )

    context.target = target

    return context