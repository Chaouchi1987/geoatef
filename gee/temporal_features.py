from __future__ import annotations
import ee
import pandas as pd
import numpy as np
from backend.gee.ee_init import init_ee
from backend.gee.temporal_sampler import get_sentinel_period
from backend.processing.grid import make_aoi_geometry, make_point_grid

SPECTRAL_FIELDS = ["ndvi", "ndwi", "ndbi", "iron", "clay"]
LULC_FIELDS = ["water", "trees", "grass", "flooded_vegetation", "crops", "shrub_and_scrub", "built", "bare"]
# Calendar quarters provide complete, repeatable seasonal windows without
# silently dropping December or creating cross-year date ambiguity.
SEASONS = (("Q1", 1, 3), ("Q2", 4, 6), ("Q3", 7, 9), ("Q4", 10, 12))


def _joined_sentinel(geometry, start, end, cloud_pct):
    s2 = get_sentinel_period(start, end, geometry, cloud_pct)
    clouds = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")
    joined = ee.ImageCollection(ee.Join.saveFirst("cloud_prob").apply(
        s2, clouds, ee.Filter.equals(leftField="system:index", rightField="system:index")
    ))
    return joined.filter(ee.Filter.notNull(["cloud_prob"]))


def _mask_s2(image):
    qa = image.select("QA60")
    qa_clear = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
    cloud = ee.Image(image.get("cloud_prob"))
    return image.updateMask(qa_clear.And(cloud.select("probability").lt(40))).divide(10000)


def _image_features(collection):
    image = collection.map(_mask_s2).median()
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("ndvi")
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("ndwi")
    ndbi = image.normalizedDifference(["B11", "B8"]).rename("ndbi")
    iron = image.select("B4").divide(image.select("B2").max(0.0001)).rename("iron")
    clay = image.select("B11").divide(image.select("B12").max(0.0001)).rename("clay")
    return image.addBands([ndvi, ndwi, ndbi, iron, clay])


def _year_features(geometry, year, cloud_pct):
    # Build all seasonal collections first, then retrieve the 8 season counts
    # in two server calls (S2 + Dynamic World). This avoids dozens of redundant
    # Earth Engine round-trips while preserving per-season auditability.
    specs=[]
    for season, start_month, end_month in SEASONS:
        if end_month == 12:
            next_start=f"{year+1}-01-01"
        else:
            next_start=f"{year}-{end_month+1:02d}-01"
        start=f"{year}-{start_month:02d}-01"
        s2=ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(geometry).filterDate(start,next_start).filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE",float(cloud_pct)))
        dw=ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterBounds(geometry).filterDate(start,next_start)
        specs.append((season,start,next_start,s2,dw))
    s2_counts=ee.List([x[3].size() for x in specs]).getInfo()
    dw_counts=ee.List([x[4].size() for x in specs]).getInfo()
    joined_specs=[]
    for season,start,end,s2,dw in specs:
        if int(s2_counts[len(joined_specs)])==0:
            joined_specs.append((season,start,end,None,dw))
            continue
        joined_specs.append((season,start,end,_joined_sentinel(geometry,start,end,cloud_pct),dw))
    # One server round-trip for all cloud-matched seasonal counts in this year.
    joined_counts=ee.List([x[3].size() if x[3] is not None else ee.Number(0) for x in joined_specs]).getInfo()
    outputs=[]
    for (season,start,end,joined,dw),s2_count,dw_count,effective_count in zip(joined_specs,s2_counts,dw_counts,joined_counts):
        if int(s2_count)==0 or int(effective_count)==0:
            continue
        image=_image_features(joined)
        if int(dw_count)>0:
            image=image.addBands(dw.select(LULC_FIELDS).median())
        outputs.append((season,image,int(effective_count),int(dw_count)))
    if not outputs:
        raise RuntimeError(f"No cloud-matched Sentinel-2 observations for year {year}.")
    return outputs

def _sample_year(geometry, points, year, cloud_pct):
    rows = []
    scene_count = 0
    dw_count = 0
    for season, image, s2_count, dw_n in _year_features(geometry, year, cloud_pct):
        scene_count += s2_count
        dw_count += dw_n
        fc = image.reduceRegions(collection=points, reducer=ee.Reducer.mean(), scale=10, tileScale=2).getInfo()
        for f in fc.get("features", []):
            p = f.get("properties") or {}
            cid = p.get("cell_id")
            if cid:
                rows.append({"cell_id": cid, "season": season, **{k: p.get(k) for k in SPECTRAL_FIELDS + LULC_FIELDS}})
    return pd.DataFrame(rows), scene_count, dw_count


def _seasonal_mean(df, field, seasons):
    if df.empty or field not in df.columns:
        return pd.Series(dtype=float)
    x=df[df["season"].isin(seasons)].groupby("cell_id")[field].mean()
    return pd.to_numeric(x, errors="coerce")


def get_grid_temporal_features(aoi, scale_m=10, start_year=2018, end_year=2025, cloud_pct=20):
    init_ee()
    radius=max(float(aoi["radius_m"]),50.0,float(scale_m)*3.0)
    geometry=make_aoi_geometry(float(aoi["latitude"]),float(aoi["longitude"]),radius,aoi.get("geometry_type","circle"))
    points=make_point_grid(geometry,int(scale_m))
    yearly={}; scene_counts={}; dw_counts={}
    for year in range(start_year,end_year+1):
        df,scenes,dw=_sample_year(geometry,points,year,cloud_pct)
        yearly[year]=df; scene_counts[year]=scenes; dw_counts[year]=dw
    ids=sorted(set().union(*[set(d.cell_id) for d in yearly.values() if not d.empty]))
    if not ids: raise RuntimeError("No temporal/LULC cells were returned from Earth Engine.")
    years=sorted(yearly); base=years[:min(3,len(years))]; recent=years[-min(3,len(years)):]
    result=pd.DataFrame(index=ids)
    for y,d in yearly.items():
        for col in SPECTRAL_FIELDS+LULC_FIELDS:
            # Keep per-season measurements available for audit/debugging.
            for season in [x[0] for x in SEASONS]:
                sub=d[d.season==season].set_index("cell_id") if not d.empty else pd.DataFrame()
                result[f"{col}_{y}_{season}"]=sub[col] if col in sub else np.nan
    def period_mean(field,ys):
        cols=[f"{field}_{y}_{season}" for y in ys for season,_,_ in SEASONS]
        return result[cols].mean(axis=1)
    # Compare the same seasonal structure in early and recent years.
    base_ndvi=period_mean("ndvi",base); recent_ndvi=period_mean("ndvi",recent)
    base_ndbi=period_mean("ndbi",base); recent_ndbi=period_mean("ndbi",recent)
    base_ndwi=period_mean("ndwi",base); recent_ndwi=period_mean("ndwi",recent)
    result["temporal_disturbance_score"]=(0.50*((base_ndvi-recent_ndvi)/0.40).clip(0,1)+0.35*((recent_ndbi-base_ndbi)/0.30).clip(0,1)+0.15*((recent_ndwi-base_ndwi).abs()/0.40).clip(0,1)).clip(0,1)
    def mean_lulc(field,ys): return period_mean(field,ys)
    built_rise=(mean_lulc("built",recent)-mean_lulc("built",base)).clip(0,1)
    crop_change=(mean_lulc("crops",recent)-mean_lulc("crops",base)).abs().clip(0,1)
    tree_change=(mean_lulc("trees",recent)-mean_lulc("trees",base)).abs().clip(0,1)
    water_change=(mean_lulc("water",recent)-mean_lulc("water",base)).abs().clip(0,1)
    result["built_change_score"]=built_rise; result["crop_change_score"]=crop_change; result["tree_change_score"]=tree_change; result["water_change_score"]=water_change
    result["possible_human_surface_change"]=(built_rise>=0.35)|((crop_change>=0.45)&(result["temporal_disturbance_score"]>=0.40))
    stabilities=[]
    for _,row in result.iterrows():
        local=[]
        for col in ("iron","clay"):
            vals=pd.to_numeric([row.get(f"{col}_{y}_{season}") for y in years for season,_,_ in SEASONS],errors="coerce")
            vals=vals[np.isfinite(vals)]
            if len(vals)>=6 and abs(float(np.mean(vals)))>1e-9:
                cv=float(np.std(vals)/abs(np.mean(vals))); local.append(max(0.0,1.0-min(cv,1.0)))
        stabilities.append(float(np.mean(local)) if local else np.nan)
    result["temporal_stability_score"]=stabilities
    result["temporal_observation_years"]=len(years); result["dynamic_world_scene_counts"]=str(dw_counts); result["sentinel_scene_counts_by_year"]=str(scene_counts)
    return result.reset_index()


def get_yearly_features(lat, lon, start_year=2018, end_year=2025, radius_m=50, cloud_pct=20):
    """Legacy point-summary adapter using the same cloud-masked seasonal Sentinel path.

    It exists only for old orchestrators; the production API uses the per-cell grid
    function above. Returned values are observations/proxies, not probabilities.
    """
    init_ee()
    area=ee.Geometry.Point([float(lon),float(lat)]).buffer(float(radius_m))
    results=[]
    for year in range(start_year,end_year+1):
        seasonal=[]
        for _, image, _, _ in _year_features(area,year,cloud_pct):
            vals=image.select(SPECTRAL_FIELDS).reduceRegion(reducer=ee.Reducer.mean(),geometry=area,scale=10,maxPixels=1e8).getInfo()
            seasonal.append(vals)
        if not seasonal:
            continue
        row={"year":year}
        for field in SPECTRAL_FIELDS:
            values=[v.get(field) for v in seasonal if v.get(field) is not None]
            row[field]=float(np.mean(values)) if values else None
        results.append(row)
    if not results:
        raise RuntimeError("No valid yearly Sentinel-2 observations were returned for the requested point.")
    return results
