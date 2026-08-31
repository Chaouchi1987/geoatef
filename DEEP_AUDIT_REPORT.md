# GeoAnomaly Pro — Deep Audit Manifest

- Python source files reviewed: **145**
- Syntax failures: **0**
- Static import cycles: **0**
- Active production analysis path: `backend/api/analysis.py`
- Earth Engine: real authenticated data required for live validation

## Scientific gates
- Sentinel-2 SR Harmonized: real scene acquisition + AOI filtering
- Dynamic World V1: 10 m land-cover probabilities for surface context and historical change
- SRTM: 30 m terrain context
- Landsat 8/9 LST: 30 m thermal context; never presented as 10 m thermal
- Iron/clay: spectral proxies; never direct mineral/gold identification
- Scores: relative evidence ranking, not probability
- Satellite-only depth/subsurface confirmation: prohibited

## Legacy policy
Legacy/orchestrator engines remain in the project for audit and reuse, but unsafe fixed-score paths are isolated from the production fusion until they pass the same scientific contract.
