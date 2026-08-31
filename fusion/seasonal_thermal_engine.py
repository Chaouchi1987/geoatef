from __future__ import annotations

def build_seasonal_score(summer_temp, winter_temp):
    """Legacy seasonal-delta helper; compatibility only, not a probability."""
    delta=round(float(summer_temp)-float(winter_temp),2)
    score=40.0 + 60.0*min(max(delta,0.0)/20.0,1.0)
    return {"seasonal_delta":delta,"seasonal_score":round(score,2)}
