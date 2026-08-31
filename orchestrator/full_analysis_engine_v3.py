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


def run_full_analysis_v3(

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

    # ---------------------------------
    # Temporal Pipeline
    # ---------------------------------

    context.temporal = run_temporal_pipeline(

        lat=lat,

        lon=lon

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

    return context