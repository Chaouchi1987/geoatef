"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.fusion.geology_engine import (
    build_geology_score
)


def run_geology_pipeline(
    df
):

    result = build_geology_score(
        df
    )

    return result