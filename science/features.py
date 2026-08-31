from __future__ import annotations
import numpy as np
import pandas as pd

SPECTRAL_FEATURES = ["ndvi","ndmi","ndwi","ndbi","iron_oxide","clay_ratio"]
TERRAIN_FEATURES = ["elevation","slope","aspect"]
ALL_FEATURES = SPECTRAL_FEATURES + TERRAIN_FEATURES

def clean_feature_matrix(df: pd.DataFrame, features: list[str] | None = None):
    features = features or [c for c in ALL_FEATURES if c in df.columns]
    x = df[features].apply(pd.to_numeric, errors="coerce")
    valid = np.isfinite(x).all(axis=1)
    return x.loc[valid], valid, features

def feature_quality(df: pd.DataFrame, features: list[str] | None = None) -> dict:
    features = features or [c for c in ALL_FEATURES if c in df.columns]
    total = max(len(df), 1)
    completeness = {}
    for c in features:
        if c not in df:
            completeness[c] = 0.0
        else:
            completeness[c] = float(df[c].notna().mean())
    return {
        "sample_count": len(df),
        "feature_count": len(features),
        "overall_completeness": float(np.mean(list(completeness.values()))) if completeness else 0.0,
        "by_feature": completeness,
        "finite_rows": int(sum(np.isfinite(df[features].apply(pd.to_numeric, errors="coerce")).all(axis=1))) if features else 0,
    }
