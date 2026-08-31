def estimate_target_center(
    targets
):

    if len(targets) == 0:

        return None

    lat = sum(
        t.lat
        for t in targets
    ) / len(targets)

    lon = sum(
        t.lon
        for t in targets
    ) / len(targets)

    return {

        "lat": round(lat, 6),

        "lon": round(lon, 6)

    }