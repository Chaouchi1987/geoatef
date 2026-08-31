from __future__ import annotations
import ee
import pandas as pd
from backend.processing.grid import make_square_geometry, make_point_grid
from backend.gee.sentinel2 import build_sentinel2_composite
from backend.gee.dem import build_dem_features

def run_real_sentinel2_analysis(aoi: dict, start_date: str, end_date: str, cloud_pct: float, scale_m: int, context_radius_m: float | None = None):
    # The requested radius is the target/AOI size. Small targets need a larger real
    # spatial context for statistics; this does not change the target geometry.
    context_radius = max(float(aoi["radius_m"]), float(context_radius_m or 0), 50.0, float(scale_m) * 3.0)
    from backend.processing.grid import make_aoi_geometry
    geometry = make_aoi_geometry(
        aoi["latitude"], aoi["longitude"], context_radius,
        aoi.get("geometry_type", "circle")
    )
    image, observation_count = build_sentinel2_composite(
        geometry, start_date, end_date, cloud_pct
    )
    dem = build_dem_features(geometry)
    feature_image = image.addBands(dem)

    points = make_point_grid(geometry, scale_m)
    sampled = feature_image.sampleRegions(
        collection=points,
        scale=scale_m,
        geometries=True,
        tileScale=2,
    )

    info = sampled.getInfo()
    rows = []
    for f in info.get("features", []):
        props = f.get("properties", {})
        geom = f.get("geometry") or {}
        coords = geom.get("coordinates") or []
        if len(coords) >= 2:
            rows.append({
                "cell_id": props.get("cell_id"),
                "grid_lon": props.get("grid_lon"),
                "grid_lat": props.get("grid_lat"),
                "lon": float(coords[0]),
                "lat": float(coords[1]),
                **{k: props.get(k) for k in [
                    "ndvi","ndmi","ndwi","ndbi",
                    "iron_oxide","clay_ratio",
                    "elevation","slope","aspect"
                ]}
            })

    if not rows:
        raise RuntimeError("Earth Engine returned no valid samples for the requested AOI and scale.")
    df = pd.DataFrame(rows)
    if df["cell_id"].isna().any() or df["cell_id"].duplicated().any():
        raise RuntimeError("Canonical cell identity was lost or duplicated during Earth Engine sampling.")
    return df, observation_count, context_radius
