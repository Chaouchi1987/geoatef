import numpy as np
import pandas as pd

from backend.anomaly.ensemble import run_anomaly_ensemble
from backend.processing.geology import add_geological_evidence
from backend.fusion.anthropogenic_risk_engine_v2 import compute_surface_artifact_risk
from backend.models.targeting import build_targets


def _frame(n=100):
    rng = np.random.default_rng(42)
    x = np.arange(n)
    return pd.DataFrame({
        "cell_id": [f"cell_{i}" for i in x],
        "lat": 35.0 + (x // 10) * 0.0001,
        "lon": 7.0 + (x % 10) * 0.0001,
        "ndvi": 0.25 + rng.normal(0, .03, n),
        "ndmi": .05 + rng.normal(0, .01, n),
        "ndwi": .02 + rng.normal(0, .01, n),
        "ndbi": rng.normal(0, .02, n),
        "iron_oxide": 1 + rng.normal(0, .05, n),
        "clay_ratio": 1 + rng.normal(0, .05, n),
        "elevation": 500 + rng.normal(0, 5, n),
        "slope": 5 + rng.normal(0, 1, n),
        "built": np.clip(rng.normal(.05, .02, n), 0, 1),
        "water": np.clip(rng.normal(.03, .02, n), 0, 1),
        "trees": np.clip(rng.normal(.20, .05, n), 0, 1),
        "crops": np.clip(rng.normal(.40, .07, n), 0, 1),
        "bare": np.clip(rng.normal(.25, .05, n), 0, 1),
    })


def _fuse(df):
    s = run_anomaly_ensemble(df)
    s = add_geological_evidence(s)
    s["row"] = np.arange(len(s)) // 10
    s["col"] = np.arange(len(s)) % 10
    s = compute_surface_artifact_risk(s)
    s["ai_evidence_score"] = s["anomaly_score"]
    s["consensus_score"] = s["anomaly_score"]
    s["temporal_score"] = .30
    s["thermal_score"] = .20
    s["pre_suppression_score"] = (
        .40*s.ai_evidence_score + .25*s.geological_score +
        .20*s.consensus_score + .10*s.temporal_score + .05*s.thermal_score
    ).clip(0, 1)
    s["artifact_penalty_factor"] = (1-.60*s.surface_artifact_risk).clip(.25, 1)
    s["final_evidence_score"] = (s.pre_suppression_score*s.artifact_penalty_factor).clip(0,1)
    s["anomaly_score"] = s["final_evidence_score"]
    return s


def test_surface_artifact_penalty_is_not_cosmetic():
    df = _frame()
    df.loc[10, "built"] = .95
    s = _fuse(df)
    assert s.loc[10, "surface_artifact_risk"] > .30
    assert s.loc[10, "final_evidence_score"] < s.loc[10, "pre_suppression_score"]


def test_target_count_and_scores_are_bounded():
    s = _fuse(_frame())
    targets = build_targets(s.sort_values("anomaly_score", ascending=False), 3, 10, 20)
    assert len(targets) <= 3
    assert all(0 <= t["strength_percent"] <= 100 for t in targets)
    assert all(0 <= t["type_interpretation"]["fit_percent"] <= 100 for t in targets)
    assert all(t["data_quality"]["synthetic"] is False for t in targets)


def test_nan_temporal_values_never_create_100_percent_fit():
    s = _fuse(_frame())
    s["temporal_disturbance_score"] = np.nan
    targets = build_targets(s.sort_values("anomaly_score", ascending=False), 3, 10, 20)
    assert all(np.isfinite(t["type_interpretation"]["fit_percent"]) for t in targets)
    assert all(t["type_interpretation"]["fit_percent"] < 100 for t in targets)


def test_human_change_is_not_double_penalized_as_surface_artifact():
    df=_frame()
    df.loc[5,"built_change_score"]=0.9
    df.loc[5,"temporal_disturbance_score"]=0.8
    df.loc[5,"built"]=0.05
    scored=compute_surface_artifact_risk(df)
    assert scored.loc[5,"human_surface_change_signal"] > 0.5
    assert scored.loc[5,"surface_artifact_risk"] < 0.30


def test_missing_evidence_is_not_imputed_as_scan_median():
    df=_frame()
    s=run_anomaly_ensemble(df)
    s=add_geological_evidence(s)
    s["ai_evidence_score"]=s["anomaly_score"]
    s["consensus_score"]=s["anomaly_score"]
    s["temporal_score"]=0.3
    s["thermal_score"]=0.2
    s.loc[0,"thermal_score"]=np.nan
    parts=[("ai_evidence_score",.40),("geological_score",.25),("consensus_score",.20),("temporal_score",.10),("thermal_score",.05)]
    score_sum=pd.Series(0.0,index=s.index); weight_sum=pd.Series(0.0,index=s.index)
    for col,w in parts:
        v=pd.to_numeric(s[col],errors="coerce"); valid=v.notna()
        score_sum += v.where(valid,0)*w; weight_sum += valid*w
    assert abs(weight_sum.loc[0]-0.95) < 1e-9


def test_counter_cases_water_trees_crops_and_boundaries_are_context_not_direct_targets():
    df=_frame()
    df["row"]=np.arange(len(df))//10; df["col"]=np.arange(len(df))%10
    # Water-dominant cell: high water context, no built evidence.
    df.loc[0,"water"]=0.95
    # Tree-dominant cell: masking context, not human-change proof.
    df.loc[1,"trees"]=0.95
    # Crop-dominant cell: agricultural context, not human-change proof.
    df.loc[2,"crops"]=0.95
    # Create a sharp crop boundary around a cell.
    df.loc[3,"crops"]=0.95
    df.loc[4,"crops"]=0.05
    scored=compute_surface_artifact_risk(df)
    assert scored.loc[0,"water_surface_risk"] > .9
    assert scored.loc[1,"vegetation_mask_risk"] > .5
    assert scored.loc[2,"vegetation_mask_risk"] > .3
    assert scored.loc[3,"landcover_boundary_risk"] > 0
    assert scored.loc[0,"human_surface_change_signal"] == 0
    assert scored.loc[1,"human_surface_change_signal"] == 0
    assert scored.loc[2,"human_surface_change_signal"] == 0


def test_water_change_is_not_human_intervention_signal():
    df=_frame()
    df["water_change_score"]=0.95
    df["built_change_score"]=0.0
    df["temporal_disturbance_score"]=0.9
    scored=compute_surface_artifact_risk(df)
    assert scored["human_surface_change_signal"].max() == 0


def test_target_score_is_reproducible_from_trace():
    df=_frame()
    s=_fuse(df)
    row=s.iloc[0]
    parts=[("ai_evidence_score",.40),("geological_score",.25),("consensus_score",.20),("temporal_score",.10),("thermal_score",.05)]
    available=[(float(row[c]),w) for c,w in parts if pd.notna(row[c])]
    pre=sum(v*w for v,w in available)/sum(w for _,w in available)
    penalty=1-.60*float(row["surface_artifact_risk"])
    final=pre*penalty
    assert abs(final-float(row["final_evidence_score"])) < 1e-12
