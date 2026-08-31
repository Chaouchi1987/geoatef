from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "ndvi", "ndmi", "ndwi", "ndbi",
    "iron_oxide", "clay_ratio",
    "elevation", "slope"
]

def robust_z_score(series: pd.Series) -> pd.Series:
    x = series.astype(float)
    med = x.median()
    mad = (x - med).abs().median()
    if not np.isfinite(mad) or mad == 0:
        std = x.std(ddof=0)
        if not np.isfinite(std) or std == 0:
            return pd.Series(np.zeros(len(x)), index=x.index)
        return (x - x.mean()) / std
    return 0.6745 * (x - med) / mad

def run_anomaly_ensemble(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    usable = [c for c in FEATURES if c in df.columns]
    clean = df[usable].replace([np.inf, -np.inf], np.nan).dropna()
    if len(clean) < 5:
        raise ValueError("Insufficient valid samples for anomaly analysis.")

    X = StandardScaler().fit_transform(clean)

    iso = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )
    iso_raw = -iso.fit(X).score_samples(X)

    # LOF requires n_neighbors < n_samples. Skip safely when sample count is too small.
    lof_raw = np.zeros(len(clean))
    if len(clean) >= 6:
        k = min(20, len(clean) - 1)
        lof = LocalOutlierFactor(n_neighbors=k, contamination="auto")
        lof.fit_predict(X)
        lof_raw = -lof.negative_outlier_factor_

    z_matrix = np.vstack([np.abs(robust_z_score(clean[c]).to_numpy()) for c in usable]).T
    z_raw = np.nanmean(z_matrix, axis=1)

    def minmax(v):
        v = np.asarray(v, dtype=float)
        lo, hi = np.nanmin(v), np.nanmax(v)
        if hi <= lo:
            return np.zeros_like(v)
        return (v - lo) / (hi - lo)

    iso_s = minmax(iso_raw)
    lof_s = minmax(lof_raw)
    z_s = minmax(z_raw)

    score = 0.45 * iso_s + 0.30 * lof_s + 0.25 * z_s

    clean = clean.copy()
    clean["isolation_forest_score"] = iso_s
    clean["lof_score"] = lof_s
    clean["zscore_score"] = z_s
    clean["anomaly_score"] = score

    df.loc[clean.index, clean.columns] = clean
    return df
