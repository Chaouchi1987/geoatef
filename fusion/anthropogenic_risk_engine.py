"""Compatibility shim for the legacy anthropogenic-risk module.

The active scientific pipeline lives in `anthropogenic_risk_engine_v2`.
This module intentionally contains no self-import and no fixed AI score.
"""
from backend.fusion.anthropogenic_risk_engine_v2 import compute_surface_artifact_risk


def build_anthropogenic_risk(zone_points):
    """Legacy adapter: return a conservative risk summary for zone points."""
    import pandas as pd
    if isinstance(zone_points, pd.DataFrame):
        df = zone_points.copy()
    else:
        df = pd.DataFrame(zone_points)
    scored = compute_surface_artifact_risk(df)
    risk = float(scored["surface_artifact_risk"].mean() * 100) if len(scored) else 0.0
    return {"risk": round(risk, 2), "reasons": []}
