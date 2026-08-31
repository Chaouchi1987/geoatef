CACHE = {}


def make_key(
    lat,
    lon
):

    return (

        round(lat, 6),

        round(lon, 6)

    )


def get_cached(
    lat,
    lon
):

    key = make_key(
        lat,
        lon
    )

    return CACHE.get(
        key
    )


def set_cached(
    lat,
    lon,
    value
):

    key = make_key(
        lat,
        lon
    )

    CACHE[key] = value