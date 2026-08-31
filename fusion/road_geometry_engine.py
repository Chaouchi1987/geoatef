import math


def build_road_geometry_risk(
    points
):

    if len(points) < 3:

        return 0

    lats = [
        p["lat"]
        for p in points
    ]

    lons = [
        p["lon"]
        for p in points
    ]

    lat_span = (
        max(lats)
        -
        min(lats)
    )

    lon_span = (
        max(lons)
        -
        min(lons)
    )

    major_axis = max(
        lat_span,
        lon_span
    )

    minor_axis = min(
        lat_span,
        lon_span
    )

    if minor_axis == 0:

        minor_axis = 0.000001

    elongation = (
        major_axis
        /
        minor_axis
    )

    risk = 0

    if elongation > 5:

        risk += 60

    elif elongation > 3:

        risk += 30

    if len(points) > 8:

        risk += 20

    return min(
        risk,
        100
    )