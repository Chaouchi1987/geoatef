"""Backward-compatible wrapper for the validated temporal Sentinel implementation."""
from backend.gee.temporal_features import get_yearly_features


def get_yearly_features_buffer(lat, lon, start_year, end_year, radius_m=50, cloud_pct=20):
    return get_yearly_features(
        lat=lat,
        lon=lon,
        start_year=start_year,
        end_year=end_year,
        radius_m=radius_m,
        cloud_pct=cloud_pct,
    )
