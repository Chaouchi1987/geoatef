from __future__ import annotations
import numpy as np
import pandas as pd

from backend.ml.isolation_forest import run_isolation_forest
from backend.ml.lof_engine import run_lof
from backend.fusion.geology_engine import build_geology_score
from backend.fusion.evidence_engine import build_evidence_scores


def prepare_legacy_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    aliases = {"iron_oxide": "iron", "clay_ratio": "clay"}
    for src, dst in aliases.items():
        if dst not in out.columns and src in out.columns:
            out[dst] = pd.to_numeric(out[src], errors="coerce")
    required = ["lat", "lon", "ndvi", "ndwi", "ndbi", "iron", "clay", "elevation", "slope"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Legacy scientific engines require missing features: {missing}")
    return out


def run_legacy_scientific_fusion(df: pd.DataFrame) -> pd.DataFrame:
    """Reuse the strongest legacy statistical/geological engines on real sampled data.

    No fixed 100-point AI score or fabricated confidence is introduced.
    """
    work = prepare_legacy_features(df)
    feature_cols = ["ndvi", "ndwi", "ndbi", "iron", "clay", "elevation", "slope"]
    model_df = work[["lat", "lon"] + feature_cols].copy()
    model_df[feature_cols] = model_df[feature_cols].apply(pd.to_numeric, errors="coerce")
    model_df = model_df.replace([np.inf, -np.inf], np.nan).dropna()
    if len(model_df) < 6:
        raise ValueError("At least 6 valid samples are required for the legacy scientific ensemble.")
    model_df[feature_cols] = model_df[feature_cols].fillna(model_df[feature_cols].median())

    iforest = run_isolation_forest(model_df)
    lof = run_lof(model_df)
    geology = build_geology_score(model_df)
    evidence = pd.DataFrame(build_evidence_scores(model_df, iforest["labels"], lof["labels"]))

    fused = model_df.merge(evidence, on=["lat", "lon"], how="left", suffixes=("", "_evidence"))
    fused = fused.merge(geology[["lat", "lon", "geology_score"]], on=["lat", "lon"], how="left")

    if_raw = np.asarray(iforest["scores"], dtype=float)
    if_score = 1.0 / (1.0 + np.exp(8.0 * if_raw))
    lof_raw = np.asarray(lof["scores"], dtype=float)
    lof_score = np.clip((-lof_raw - 1.0), 0.0, 1.0)
    evidence_score = pd.to_numeric(evidence["score"], errors="coerce").to_numpy(float) / 100.0

    fused["isolation_forest_score"] = if_score
    fused["lof_score"] = lof_score
    fused["legacy_evidence_score"] = np.clip(evidence_score, 0, 1)
    fused["ai_evidence_score"] = np.clip(
        0.45 * if_score + 0.30 * lof_score + 0.25 * np.clip(evidence_score, 0, 1), 0, 1
    )
    fused["geological_score"] = (pd.to_numeric(fused["geology_score"], errors="coerce") / 100.0).clip(0, 1)
    return fused
