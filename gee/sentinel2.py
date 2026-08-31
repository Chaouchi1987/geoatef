from __future__ import annotations
import ee

def _attach_cloud_probability(collection):
    clouds=ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")
    joined=ee.ImageCollection(ee.Join.saveFirst("cloud_prob").apply(collection,clouds,ee.Filter.equals(leftField="system:index",rightField="system:index")))
    return joined.filter(ee.Filter.notNull(["cloud_prob"]))

def mask_s2_clouds(image: ee.Image) -> ee.Image:
    qa=image.select("QA60")
    qa_clear=qa.bitwiseAnd(1<<10).eq(0).And(qa.bitwiseAnd(1<<11).eq(0))
    cloud=ee.Image(image.get("cloud_prob"))
    return image.updateMask(qa_clear.And(cloud.select("probability").lt(40))).divide(10000)

def build_sentinel2_composite(geometry: ee.Geometry,start_date: str,end_date: str,cloud_pct: float):
    collection=(ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(geometry).filterDate(start_date,end_date).filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE",float(cloud_pct))))
    raw_count=collection.size().getInfo()
    if raw_count==0: raise RuntimeError("No Sentinel-2 observations matched the AOI/date/cloud filters.")
    collection=_attach_cloud_probability(collection)
    count=collection.size().getInfo()
    if count==0: raise RuntimeError("No Sentinel-2 observations had a matching cloud-probability scene.")
    composite=collection.map(mask_s2_clouds).median()
    ndvi=composite.normalizedDifference(["B8","B4"]).rename("ndvi")
    ndmi=composite.normalizedDifference(["B8","B11"]).rename("ndmi")
    ndwi=composite.normalizedDifference(["B3","B8"]).rename("ndwi")
    ndbi=composite.normalizedDifference(["B11","B8"]).rename("ndbi")
    iron_oxide=composite.select("B4").divide(composite.select("B2").max(0.0001)).rename("iron_oxide")
    clay_ratio=composite.select("B11").divide(composite.select("B12").max(0.0001)).rename("clay_ratio")
    return composite.addBands([ndvi,ndmi,ndwi,ndbi,iron_oxide,clay_ratio]),count
