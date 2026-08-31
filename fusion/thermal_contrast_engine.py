"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from __future__ import annotations

def build_thermal_contrast(target_temp, neighborhood_temp):
    """Legacy thermal contrast helper.

    Returns a bounded *contrast score* for compatibility. It is not a probability
    and is not part of the production 30 m Landsat thermal path.
    """
    contrast=round(float(target_temp)-float(neighborhood_temp),2)
    score=50.0 + 50.0*min(abs(contrast)/5.0,1.0)
    return {"contrast":contrast,"contrast_score":round(score,2)}
