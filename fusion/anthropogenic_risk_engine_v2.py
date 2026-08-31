from __future__ import annotations
import numpy as np
import pandas as pd


def compute_surface_artifact_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate surface-context risk without pretending to identify objects.

    Priority is given to independent LULC probabilities from Dynamic World.
    NDBI/NDVI/NDWI alone are not treated as proof of buildings, roads or farms.
    """
    out = df.copy()
    for c in ("ndvi", "ndwi", "ndbi", "built_change_score", "crop_change_score",
              "tree_change_score", "water_change_score", "temporal_disturbance_score"):
        out[c] = pd.to_numeric(out[c], errors="coerce") if c in out else np.nan

    # Current surface context. Dynamic World probabilities are 0..1 at 10 m.
    for c in ("built", "water", "trees", "crops", "bare"):
        out[f"dw_{c}_prob"] = pd.to_numeric(out.get(c, np.nan), errors="coerce").clip(0, 1)

    out["built_surface_risk"] = out["dw_built_prob"].fillna(0)
    out["water_surface_risk"] = out["dw_water_prob"].fillna(0)
    # Vegetation/crops are primarily masking/context, not anthropogenic proof.
    out["vegetation_mask_risk"] = (
        0.60 * out["dw_trees_prob"].fillna(0) +
        0.40 * out["dw_crops_prob"].fillna(0)
    ).clip(0, 1)

    # Boundary risk uses actual neighboring LULC probabilities where available.
    if {"row", "col"}.issubset(out.columns):
        work = out.set_index(["row", "col"])
        risk=[]
        for r,c in zip(out["row"],out["col"]):
            neighbors=[]
            center=[]
            for band in ("built","crops","trees","water","bare"):
                center.append(float(work[band].get((r,c),np.nan)) if band in work else np.nan)
            for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                if (r+dr,c+dc) in work.index:
                    for band in ("built","crops","trees","water","bare"):
                        neighbors.append(abs(float(work[band].get((r+dr,c+dc),np.nan))-float(work[band].get((r,c),np.nan))))
            vals=[v for v in neighbors if np.isfinite(v)]
            risk.append(float(np.clip(np.mean(vals) if vals else 0,0,1)))
        out["landcover_boundary_risk"] = risk
    else:
        out["landcover_boundary_risk"] = 0.0

    # Human-change hypothesis is separated from static context.
    # A water change is deliberately NOT treated as human intervention.
    # Crop change is retained as land-use context; only a built-up transition
    # contributes to the human-surface-change hypothesis in this conservative model.
    out["land_use_change_signal"] = out["crop_change_score"].fillna(0).clip(0,1)
    out["human_surface_change_signal"] = out["built_change_score"].fillna(0).clip(0,1)

    # Static/context artifacts are penalized. Historical human-surface change is
    # retained as independent evidence and must NOT penalize itself.
    out["surface_artifact_risk"] = (
        0.40*out["built_surface_risk"] +
        0.25*out["water_surface_risk"] +
        0.20*out["vegetation_mask_risk"] +
        0.15*out["landcover_boundary_risk"]
    ).clip(0,1)

    out["surface_context_reasons"] = out.apply(lambda r: "; ".join([
        x for x in [
            "built-up land-cover probability is high" if r["built_surface_risk"] >= .60 else "",
            "water/moisture land-cover probability is high" if r["water_surface_risk"] >= .60 else "",
            "trees/crops may mask surface spectral evidence" if r["vegetation_mask_risk"] >= .55 else "",
            "sharp land-cover boundary detected" if r["landcover_boundary_risk"] >= .50 else "",
            "historical built-up surface change signal" if r["human_surface_change_signal"] >= .55 else "",
            "historical crop/land-use change context" if r["land_use_change_signal"] >= .45 else "",
        ] if x
    ]) or "No strong surface-context penalty", axis=1)
    return out
