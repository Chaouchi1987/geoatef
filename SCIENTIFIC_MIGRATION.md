# GeoAnomaly Pro — Scientific Core Migration

The uploaded legacy GeoAnomaly source archive has been integrated into the new authenticated platform.

## Integrated legacy source groups

- `anomaly/`
- `contracts/`
- `fusion/`
- `gee/`
- `ml/`
- `orchestrator/`
- `services/`
- `cache/`
- legacy report/target models

## Production path

The production API now uses:

1. Real Earth Engine Sentinel-2 + DEM acquisition.
2. Current robust anomaly ensemble.
3. Legacy Isolation Forest + LOF engines.
4. Legacy geological scoring.
5. Legacy evidence fusion.
6. Multi-scale spatial consensus.
7. Optional historical Sentinel temporal analysis.
8. Optional Landsat thermal contrast analysis.
9. Evidence-based target ranking.

## Important audit decisions

Some legacy orchestrators were experimental. In particular, `full_analysis_engine_v4.py` contains fixed `ai_score=100` and `structural_score=0`; it is **not used by the production API**.

No fixed AI score, fabricated confidence, random target, or synthetic heatmap is used by the current production analysis endpoint.

## Earth Engine user isolation

Legacy `gee/ee_init.py` was rewritten so legacy engines obtain the authenticated user's Earth Engine authorization through the current OAuth/auth layer. The Python Earth Engine client is process-global, so analyses are serialized around initialization in the local backend. A production deployment should run analysis jobs in isolated worker processes.
