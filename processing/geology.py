from __future__ import annotations
import numpy as np
import pandas as pd


def _robust_abs_score(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    med = x.median()
    mad = (x - med).abs().median()
    if not np.isfinite(mad) or mad <= 0:
        sd = x.std(ddof=0)
        if not np.isfinite(sd) or sd <= 0:
            return pd.Series(np.zeros(len(x)), index=x.index)
        z = (x - x.mean()).abs() / sd
    else:
        z = (0.6745 * (x - med) / mad).abs()
    return (z / 4.0).clip(0, 1)


def add_geological_evidence(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a relative spectral-proxy anomaly, not a mineral probability.

    Iron-oxide and clay ratios are remote-sensing proxies. Terrain and land-cover
    are deliberately excluded from this geological proxy so that unrelated
    elevation/slope heuristics cannot masquerade as mineral evidence.
    """
    out = df.copy()
    parts = []
    for col in ("iron_oxide", "clay_ratio"):
        if col in out.columns:
            parts.append(_robust_abs_score(out[col]))
    out["geological_score"] = (
        np.nanmean(np.vstack([p.to_numpy(float) for p in parts]), axis=0)
        if parts else np.nan
    )
    out["geological_evidence_type"] = "relative spectral-proxy anomaly"
    return out
