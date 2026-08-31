"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.orchestrator.full_analysis_engine_v4 import (
    run_full_analysis_v4
)

from backend.orchestrator.structural_pipeline import (
    run_structural_pipeline
)

from backend.orchestrator.ai_pipeline import (
    run_ai_pipeline
)


def run_target_scan(

    cells,

    start_date="2025-01-01",

    end_date="2025-12-31"

):

    targets = []

    for cell in cells:

        try:

            context = run_full_analysis_v4(

                cells=[cell],

                lat=cell["lat"],

                lon=cell["lon"],

                start_date=start_date,

                end_date=end_date

            )

            targets.append(
                context.target
            )

        except Exception as e:

            print(
                "TARGET FAILED:",
                cell,
                str(e)
            )

    # -------------------------
    # Structural Intelligence
    # -------------------------

    if len(targets) >= 3:

        structural = run_structural_pipeline(
            targets
        )

        for target in targets:

            target.structural_score = (
                structural.structural_score
            )

            ai_result = run_ai_pipeline(

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

            target.intelligence_score = (
                ai_result[
                    "intelligence_score"
                ]
            )

            target.category = (
                ai_result[
                    "category"
                ]
            )

            target.confidence = (
                ai_result[
                    "confidence"
                ]
            )

            target.reasons = (
                ai_result[
                    "reasons"
                ]
            )

    return targets