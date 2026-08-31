"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.fusion.structural_anomaly_engine import (
    detect_linear_patterns
)

from backend.fusion.target_geometry_engine import (
    estimate_target_diameter
)

from backend.contracts.structural_result import (
    StructuralResult
)


def run_structural_pipeline(
    targets
):

    # -------------------------
    # Linear Pattern Detection
    # -------------------------

    patterns = detect_linear_patterns(
        targets
    )

    linear_penalty = min(

        len(patterns) * 20,

        60

    )

    # -------------------------
    # Geometry Analysis
    # -------------------------

    diameter = estimate_target_diameter(
        targets
    )

    if diameter <= 5:

        geometry_score = 100

    elif diameter <= 10:

        geometry_score = 90

    elif diameter <= 20:

        geometry_score = 80

    elif diameter <= 30:

        geometry_score = 60

    elif diameter <= 50:

        geometry_score = 30

    elif diameter <= 100:

        geometry_score = 10

    else:

        geometry_score = 0

    # -------------------------
    # Final Structural Score
    # -------------------------

    structural_score = max(

        geometry_score

        -

        linear_penalty,

        0

    )

    result = StructuralResult()

    result.structural_score = (
        structural_score
    )

    result.pattern_score = (
        len(patterns)
    )

    result.geometry_score = (
        geometry_score
    )

    result.diameter_m = (
        diameter
    )

    result.patterns = (
        patterns
    )

    print(
        "DIAMETER =",
        diameter
    )

    print(
        "LINEAR PATTERNS =",
        len(patterns)
    )

    print(
        "LINEAR PENALTY =",
        linear_penalty
    )

    print(
        "GEOMETRY SCORE =",
        geometry_score
    )

    print(
        "STRUCTURAL SCORE =",
        structural_score
    )

    return result