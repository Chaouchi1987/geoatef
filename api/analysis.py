from __future__ import annotations
from fastapi import APIRouter, HTTPException, Request
import pandas as pd
from backend.models.schemas import AnalysisStartRequest
from backend.gee.auth import initialize_for_user, earth_engine_status
from backend.gee.ee_init import set_ee_user, reset_ee_user, analysis_lock
from backend.anomaly.ensemble import run_anomaly_ensemble
from backend.processing.geology import add_geological_evidence
from backend.science.multiscale import neighborhood_consensus
from backend.science.features import feature_quality
from backend.models.targeting import build_targets
from backend.core.store import AOIS, RUNS, RESULTS
from backend.core.auth import current_user, ee_connected
import uuid, threading, traceback, hashlib, json
from datetime import datetime, timezone
from backend.science.utm import wgs84_to_utm
from backend.processing.grid import make_aoi_geometry

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _run(analysis_id: str, req: AnalysisStartRequest, user_id: str):
    state = RUNS[analysis_id]
    token = None
    lock = analysis_lock()

    def stage(name, progress, message):
        state.update(status="running", stage=name, progress=progress, message=message)
        print(f"[GeoAnomaly] {analysis_id} | {name} | {progress:.0%} | {message}", flush=True)

    try:
        token = set_ee_user(user_id)
        stage("queued", 0.01, "Analysis worker started; waiting for Earth Engine analysis slot.")

        acquired = lock.acquire(timeout=15)
        if not acquired:
            raise RuntimeError(
                "Earth Engine analysis worker is busy or locked by another analysis. "
                "No result was generated. Restart the backend and retry."
            )

        try:
            stage("acquisition", 0.05,
                  "Connecting to the authenticated user's Earth Engine authorization.")
            aoi = AOIS.get(req.aoi_id)
            if not aoi:
                raise RuntimeError("AOI was not found in the current backend session.")

            if not initialize_for_user(user_id):
                status = earth_engine_status(user_id)
                raise RuntimeError(status.get("message") or "Earth Engine authorization failed.")

            stage("spectral_dem", 0.20,
                  "Acquiring real Sentinel-2 and SRTM DEM observations.")
            from backend.gee.analysis import run_real_sentinel2_analysis
            df, observation_count, context_radius_m = run_real_sentinel2_analysis(
                aoi, req.start_date, req.end_date, req.cloud_pct, req.scale_m
            )
            print(f"[GeoAnomaly] {analysis_id} | samples={len(df)} observations={observation_count}", flush=True)
            if len(df) < 6:
                raise RuntimeError(
                    f"Only {len(df)} valid real samples returned in the analysis context; "
                    "at least 6 are required for the statistical ensemble."
                )

            # Canonical grid row/column indices are derived from the actual
            # server-side grid coordinates, not from row arrival order.
            for axis in ("grid_lat", "grid_lon"):
                df[axis] = pd.to_numeric(df[axis], errors="coerce")
            df["row"] = df["grid_lat"].rank(method="dense", ascending=True).astype("Int64") - 1
            df["col"] = df["grid_lon"].rank(method="dense", ascending=True).astype("Int64") - 1

            quality = feature_quality(df)

            stage("anomaly_ensemble", 0.38,
                  "Running robust Z-score, Isolation Forest and LOF.")
            scored = run_anomaly_ensemble(df)
            # The active ensemble score is the only AI/statistical evidence score
            # used in production. Legacy IF/LOF/evidence engines are not re-run.
            scored["ai_evidence_score"] = pd.to_numeric(
                scored["anomaly_score"], errors="coerce"
            ).clip(0, 1)

            stage("legacy_scientific_audit", 0.50,
                  "Keeping legacy engines isolated until each engine passes the unified scientific contract.")
            # Legacy statistical/score engines are NOT added to the final score here.
            # This prevents double-counting and avoids importing legacy fixed heuristics.
            scored["legacy_engines_status"] = "available_not_used_in_final_score"

            stage("geology", 0.60,
                  "Computing robust relative spectral-proxy anomaly from iron-oxide and clay ratios.")
            scored = add_geological_evidence(scored)
            scored["geological_score"] = pd.to_numeric(
                scored["geological_score"], errors="coerce"
            ).clip(0, 1)

            stage("multiscale", 0.72,
                  "Computing spatial consensus across multiple radii.")
            radii = tuple(sorted(set([10, req.scale_m, 50])))
            scored = neighborhood_consensus(scored, radii_m=radii)

            import numpy as np
            R = 6371000.0
            lat0 = np.radians(float(aoi["latitude"]))
            x = np.radians(pd.to_numeric(scored["lon"], errors="coerce").to_numpy(float)) * R * np.cos(lat0)
            y = np.radians(pd.to_numeric(scored["lat"], errors="coerce").to_numpy(float)) * R
            x0 = np.radians(float(aoi["longitude"])) * R * np.cos(lat0)
            y0 = np.radians(float(aoi["latitude"])) * R
            scored["distance_to_aoi_center_m"] = np.hypot(x-x0, y-y0)
            target_limit = float(aoi["radius_m"]) + float(req.scale_m)/2.0
            geometry_type = aoi.get("geometry_type", "circle")
            if geometry_type == "square":
                dlat = np.radians(pd.to_numeric(scored["lat"], errors="coerce").to_numpy(float) - float(aoi["latitude"])) * R
                dlon = np.radians(pd.to_numeric(scored["lon"], errors="coerce").to_numpy(float) - float(aoi["longitude"])) * R * np.cos(lat0)
                inside = (np.abs(dlat) <= float(aoi["radius_m"])) & (np.abs(dlon) <= float(aoi["radius_m"]))
            else:
                inside = scored["distance_to_aoi_center_m"].to_numpy(float) <= float(aoi["radius_m"])
            target_candidates = scored.loc[inside].copy()
            if target_candidates.empty:
                raise RuntimeError("No sampled cells fall inside the requested AOI; no target was fabricated outside the AOI.")

            optional = {"temporal": "not_run", "thermal": "not_run",
                        "structural": "not_run", "aster": "not_run"}

            try:
                from backend.gee.temporal_features import get_grid_temporal_features
                stage("temporal", 0.80,
                      "Comparing historical Sentinel surface signatures cell-by-cell from 2018 to 2025.")
                temporal_df = get_grid_temporal_features(
                    aoi=aoi, scale_m=req.scale_m,
                    start_year=2018, end_year=2025,
                    cloud_pct=req.cloud_pct
                )
                scored = scored.merge(temporal_df, on="cell_id", how="left", validate="one_to_one")
                temporal_stability = pd.to_numeric(scored["temporal_stability_score"], errors="coerce")
                temporal_disturbance = pd.to_numeric(scored["temporal_disturbance_score"], errors="coerce")
                temporal_weight = temporal_stability.notna().astype(float) * 0.65 + temporal_disturbance.notna().astype(float) * 0.35
                temporal_sum = temporal_stability.fillna(0) * 0.65 + temporal_disturbance.fillna(0) * 0.35
                scored["temporal_score"] = (temporal_sum / temporal_weight.replace(0, pd.NA)).clip(0, 1)
                optional["temporal"] = "available_per_cell"
            except Exception as exc:
                optional["temporal"] = f"unavailable: {str(exc)[:180]}"
                print(f"[GeoAnomaly] temporal unavailable: {exc}", flush=True)

            try:
                from backend.gee.thermal_features import get_grid_thermal_features
                stage("thermal", 0.84,
                      "Sampling real Landsat 8/9 land-surface temperature on the canonical grid.")
                thermal_df = get_grid_thermal_features(
                    aoi=aoi, scale_m=req.scale_m,
                    start_date=req.start_date, end_date=req.end_date
                )
                scored = scored.merge(thermal_df, on="cell_id", how="left", validate="one_to_one")
                scored["thermal_score"] = pd.to_numeric(
                    scored["thermal_robust_anomaly"], errors="coerce"
                ).clip(0, 1)
                optional["thermal"] = "available_per_cell"
            except Exception as exc:
                optional["thermal"] = f"unavailable: {str(exc)[:180]}"
                print(f"[GeoAnomaly] thermal unavailable: {exc}", flush=True)

            stage("artifact_suppression", 0.88,
                  "Separating surface/anthropogenic signatures from multi-source anomaly evidence.")
            from backend.fusion.anthropogenic_risk_engine_v2 import compute_surface_artifact_risk
            scored = compute_surface_artifact_risk(scored)

            stage("ranking", 0.92, "Ranking independent evidence without treating the score as probability.")
            # Fixed fusion weights. Missing modules are renormalized only over
            # modules that genuinely produced data; missing data is never zero evidence.
            parts = [
                ("ai_evidence_score", 0.40),
                ("geological_score", 0.25),
                ("consensus_score", 0.20),
                ("temporal_score", 0.10),
                ("thermal_score", 0.05),
            ]
            score_sum=pd.Series(0.0,index=scored.index)
            weight_sum=pd.Series(0.0,index=scored.index)
            for col,w in parts:
                if col not in scored.columns:
                    continue
                values=pd.to_numeric(scored[col],errors="coerce")
                valid=values.notna()
                score_sum=score_sum.add(values.where(valid,0.0)*w,fill_value=0.0)
                weight_sum=weight_sum.add(valid.astype(float)*w,fill_value=0.0)
            if not bool((weight_sum>0).any()):
                raise RuntimeError("No independent evidence modules produced a usable score.")
            scored["evidence_weight_available"]=weight_sum
            scored["pre_suppression_score"]=(score_sum/weight_sum.replace(0,pd.NA)).clip(0,1)
            scored["artifact_penalty_factor"]=(1.0-0.60*pd.to_numeric(scored["surface_artifact_risk"],errors="coerce").fillna(0)).clip(0.25,1.0)
            scored["final_evidence_score"]=(scored["pre_suppression_score"]*scored["artifact_penalty_factor"]).clip(0,1)
            scored["anomaly_score"]=scored["final_evidence_score"]
            ranked=scored.sort_values("final_evidence_score",ascending=False).copy()
            ranked_candidates=ranked.loc[inside].copy()
            if ranked_candidates.empty:
                raise RuntimeError("No ranked cells remain inside the requested AOI; no target was fabricated outside the AOI.")
            targets=build_targets(ranked_candidates,max_targets=3,scale_m=req.scale_m,min_separation_m=max(20.0,float(req.scale_m)*2.0))

            # Immutable audit trace: the exact components that produced every
            # target score are persisted so UI/report/PDF can be reconciled.
            target_by_cell = {}
            for _, row in ranked_candidates.iterrows():
                key = str(row.get("cell_id"))
                components = {}
                for col, w in parts:
                    value = pd.to_numeric(pd.Series([row.get(col)]), errors="coerce").iloc[0]
                    if pd.notna(value):
                        components[col] = {"value": float(value), "weight": float(w), "weighted": float(value*w)}
                pre = float(row.get("pre_suppression_score")) if pd.notna(row.get("pre_suppression_score")) else None
                penalty = float(row.get("artifact_penalty_factor")) if pd.notna(row.get("artifact_penalty_factor")) else None
                final = float(row.get("final_evidence_score")) if pd.notna(row.get("final_evidence_score")) else None
                trace = {"cell_id": key, "components": components, "available_weight": float(row.get("evidence_weight_available")), "pre_suppression_score": pre, "artifact_penalty_factor": penalty, "final_evidence_score": final}
                trace_json=json.dumps(trace,sort_keys=True,separators=(",",":"))
                trace["trace_id"]=hashlib.sha256(trace_json.encode("utf-8")).hexdigest()[:16]
                target_by_cell[key]=trace
            for target in targets:
                trace=target_by_cell.get(str(target.get("cell_id")))
                if trace:
                    target["score_trace"]=trace
                    target["trace_id"]=trace["trace_id"]

            duration_seconds=None
            try: duration_seconds=round((datetime.now(timezone.utc)-datetime.fromisoformat(state["started_at"])).total_seconds(),2)
            except Exception: pass
            centre_utm=wgs84_to_utm(float(aoi["latitude"]),float(aoi["longitude"]))
            RESULTS[analysis_id] = {
                "datasets": [
                    {"name":"Sentinel-2 SR Harmonized","status":"available",
                     "scenes":observation_count,"resolution_m":10,
                     "note":"scene count after AOI/date/cloud filtering; not pixel count"},
                    {"name":"SRTM DEM","status":"available","resolution_m":30},
                    {"name":"Dynamic World LULC","status":optional["temporal"],"resolution_m":10,
                     "note":"annual probability composites used for surface-context and historical-change checks"},
                    {"name":"Temporal Sentinel","status":optional["temporal"]},
                    {"name":"Landsat 8/9 Thermal","status":optional["thermal"],"resolution_m":30,
                     "note":"thermal evidence is coarse-context evidence; not a 10 m thermal measurement"},
                    {"name":"Legacy GeoAnomaly engines","status":"isolated_pending_validation",
                     "modules":["legacy engines retained for audit; not injected into final score"]},
                ],
                "samples": ranked.where(pd.notna(ranked), None).to_dict(orient="records"),
                "targets": targets,
                "quality": quality,
                "metadata": {
                    "synthetic": False,
                    "analysis_scale_m": req.scale_m,
                    "start_date": req.start_date,
                    "end_date": req.end_date,
                    "cloud_pct": req.cloud_pct,
                    "sample_count": len(ranked),
                    "target_candidate_count": len(ranked_candidates),
                    "context_radius_m": context_radius_m,
                    "observation_count": observation_count,
                    "legacy_engines_integrated": False,
                    "legacy_engines_status": "isolated_pending_engine_by_engine_validation",
                    "score_semantics": "relative evidence/anomaly score, not probability",
                    "artifact_suppression": True,
                    "optional_modules": optional,
                    "method": "real Earth Engine scenes + Sentinel-2/SRTM sampling + Dynamic World LULC + per-cell temporal comparison + Landsat 8/9 thermal context + robust statistical ensemble + spectral-proxy geology + multiscale consensus + surface-context suppression + evidence fusion",
                    "centre_utm":centre_utm,"duration_seconds":duration_seconds,"aoi_center":{"latitude":float(aoi["latitude"]),"longitude":float(aoi["longitude"])},"aoi_radius_m":float(aoi["radius_m"]),"target_box_m":10,
                    "scientific_interpretation_policy":"surface-signature interpretation only; no direct underground object/depth claim",
                    "score_calibration":"not a probability; relative evidence ranking within the analyzed AOI",
                    "thermal_effective_resolution_m":30,
                    "spectral_proxy_effective_resolution_m":20,
                    "landcover_source":"GOOGLE/DYNAMICWORLD/V1",
                    "earth_engine_request_model": {
                        "primary_sentinel": "1 collection-count + 1 cloud-joined-count + 1 reduceRegions sampling call",
                        "temporal": "server-side seasonal counts plus per-season cloud-match validation and one reduceRegions per available season",
                        "thermal": "1 reduceRegions call after collection filtering",
                        "legacy_getinfo_calls_are_not_in_production_path": True
                    },
                    "score_provenance": "Target score is persisted from final_evidence_score; target trace_id hashes its component values, weights, available weight, penalty and final score." ,
                }
            }
            stage("completed", 1.0,
                  f"Completed from {len(ranked)} real spatial samples and {observation_count} observations.")
            state["status"] = "completed"
            state["completed_at"] = datetime.now(timezone.utc).isoformat()
            state["duration_seconds"] = RESULTS[analysis_id]["metadata"].get("duration_seconds")
        finally:
            lock.release()

    except Exception as exc:
        state.update(
            status="failed", stage="failed", progress=None,
            error=str(exc), message="No scientific result was generated.",
            traceback=traceback.format_exc()
        )
        print(f"[GeoAnomaly] {analysis_id} | FAILED | {exc}", flush=True)
        print(traceback.format_exc(), flush=True)
    finally:
        if token is not None:
            reset_ee_user(token)


@router.post("/start")
def start(req: AnalysisStartRequest, request: Request):
    user=current_user(request)
    if req.scale_m not in [10,20,30,40,50]:
        raise HTTPException(400,"Supported investigation scales are 10, 20, 30, 40 and 50 meters.")
    aoi=AOIS.get(req.aoi_id)
    if not aoi or aoi.get("user_id") != user["sub"]:
        raise HTTPException(403,"AOI does not belong to the authenticated user.")
    if not ee_connected(user["sub"]):
        raise HTTPException(403,"Google Earth Engine must be connected for this user before analysis can start.")
    analysis_id=str(uuid.uuid4())
    RUNS[analysis_id]={"analysis_id":analysis_id,"user_id":user["sub"],"status":"queued","stage":"queued","progress":0.0,"error":None,"message":"Analysis queued.","started_at":datetime.now(timezone.utc).isoformat(),"completed_at":None}
    threading.Thread(target=_run,args=(analysis_id,req,user["sub"]),daemon=True).start()
    return {"analysis_id":analysis_id}

def _owned_run(analysis_id: str, request: Request):
    run=RUNS.get(analysis_id)
    if not run: raise HTTPException(404,"Analysis not found.")
    user=current_user(request)
    if run.get("user_id") != user["sub"]: raise HTTPException(403,"Analysis does not belong to the authenticated user.")
    return run

@router.get("/{analysis_id}/status")
def status(analysis_id:str, request: Request):
    return _owned_run(analysis_id,request)

@router.get("/{analysis_id}/datasets")
def datasets(analysis_id:str, request: Request):
    _owned_run(analysis_id,request)
    return {"datasets":RESULTS.get(analysis_id,{}).get("datasets",[])}

@router.get("/{analysis_id}/layers")
def layers(analysis_id:str, request: Request):
    _owned_run(analysis_id,request)
    r=RESULTS.get(analysis_id,{})
    return {"layers":[{"id":"samples","name":"Real observations","type":"points","count":len(r.get("samples",[]))},{"id":"targets","name":"Evidence-supported targets","type":"geojson","count":len(r.get("targets",[]))}]}

@router.get("/{analysis_id}/targets")
def targets(analysis_id:str, request: Request):
    _owned_run(analysis_id,request)
    return {"targets":RESULTS.get(analysis_id,{}).get("targets",[])}

@router.get("/{analysis_id}/samples")
def samples(analysis_id:str, request: Request):
    _owned_run(analysis_id,request)
    r=RESULTS.get(analysis_id,{})
    return {"samples":r.get("samples",[]),"metadata":r.get("metadata",{}),"quality":r.get("quality",{})}

@router.get("/{analysis_id}/debug")
def debug_status(analysis_id: str, request: Request):
    return _owned_run(analysis_id,request)
