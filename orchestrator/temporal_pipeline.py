"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
from backend.gee.temporal_features import (
    get_yearly_features
)

from backend.fusion.temporal_stability_engine import (
    build_temporal_stability
)


def run_temporal_pipeline(
    lat,
    lon,
    start_year=2018,
    end_year=2025
):

    yearly_features = get_yearly_features(
        lat=lat,
        lon=lon,
        start_year=start_year,
        end_year=end_year
    )

    result = build_temporal_stability(
        yearly_features
    )

    return result