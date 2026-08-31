"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _robust_abs(series: pd.Series) -> pd.Series:
    x=pd.to_numeric(series,errors="coerce")
    med=x.median(); mad=(x-med).abs().median()
    if not np.isfinite(mad) or mad<=0:
        sd=x.std(ddof=0)
        if not np.isfinite(sd) or sd<=0:return pd.Series(np.zeros(len(x)),index=x.index)
        z=(x-x.mean()).abs()/sd
    else:z=(0.6745*(x-med)/mad).abs()
    return (z/4).clip(0,1)


def build_geology_score(df: pd.DataFrame):
    """Legacy-compatible geology score using spectral proxies only.

    Terrain and land-cover are intentionally excluded. The result is a
    relative spectral-proxy anomaly, not a mineral probability.
    """
    out=df.copy(); parts=[]
    for col in ("iron","iron_oxide"):
        if col in out.columns: parts.append(_robust_abs(out[col])); break
    for col in ("clay","clay_ratio"):
        if col in out.columns: parts.append(_robust_abs(out[col])); break
    out["geology_score"]=(np.nanmean(np.vstack([p.to_numpy(float) for p in parts]),axis=0)*100 if parts else np.nan)
    return out
