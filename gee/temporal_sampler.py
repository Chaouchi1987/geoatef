from __future__ import annotations
import ee
from backend.gee.ee_init import init_ee


def get_sentinel_period(start_date, end_date, geometry=None, cloud_pct=20):
    init_ee()
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    if geometry is not None:
        collection = collection.filterBounds(geometry)
    collection = (
        collection.filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", float(cloud_pct)))
    )
    return collection
