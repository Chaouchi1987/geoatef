# GeoAnomaly Pro

**Geospatial Intelligence & Scientific Anomaly Analysis**

GeoAnomaly Pro is a research-oriented GIS and remote-sensing platform designed to identify statistically unusual geospatial signatures worthy of field investigation.

> **Scientific boundary:** GeoAnomaly Pro does not directly detect buried objects, graves, tunnels, treasure, cavities or other underground objects from satellite imagery alone. Interpretations are hypotheses that require independent validation.

## Architecture

```text
Web GIS / Leaflet
        |
        v
FastAPI
        |
        +-- User / Session layer
        +-- Earth Engine access
        +-- Raster / Surface Lab
        +-- Feature engineering
        +-- Statistical anomaly ensemble
        +-- Geological intelligence
        +-- Temporal / Thermal / Structural engines
        +-- Multi-scale consensus
        +-- Evidence fusion
        +-- Target ranking
        +-- Scientific reporting
```

## Planned scientific stack

- Google Earth Engine
- Sentinel-1 / Sentinel-2
- Landsat
- ASTER
- MODIS
- Copernicus DEM / SRTM / NASADEM
- Future EMIT integration
- Raster algebra
- Terrain analysis
- Kriging / IDW / gridding
- PCA
- Robust Z-score
- Isolation Forest
- LOF
- Spatial clustering
- Temporal stability
- Thermal contrast
- Structural/lineament analysis
- Evidence fusion
- Multi-scale consensus

## User identity and Earth Engine

GeoAnomaly Pro uses its own username/email/password identity for the application. Earth Engine access is separate and must use the user's own Google/Earth Engine authorization through OAuth. Never put a shared Earth Engine service-account private key in frontend code.

## Languages

- Arabic (RTL)
- English (LTR)

## Scientific provenance

Every final target must retain:
- source datasets
- acquisition dates
- native resolution
- analysis scale
- cloud/data-quality filters
- features
- algorithm parameters
- model version
- evidence components
- limitations

## Important

A score such as `87/100` is an anomaly/evidence score. It is not an 87% probability that a buried object exists.

## Local development

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r backend/requirements.txt
earthengine authenticate
uvicorn backend.main:app --reload
```

Serve `frontend/` with a local HTTP server. Configure `.env` from `.env.example`.

## Status

v1.0 architecture/foundation. Production release requires final OAuth configuration, durable database/session storage, deployment configuration, comprehensive scientific validation, and field-validation datasets.
