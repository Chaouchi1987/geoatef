import math


def distance_meters(
    lat1,
    lon1,
    lat2,
    lon2
):

    r = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(
        lat2 - lat1
    )

    dlambda = math.radians(
        lon2 - lon1
    )

    a = (

        math.sin(dphi / 2) ** 2

        +

        math.cos(phi1)

        *

        math.cos(phi2)

        *

        math.sin(
            dlambda / 2
        ) ** 2

    )

    c = (

        2

        *

        math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

    )

    return r * c


def get_lat(point):

    if isinstance(point, dict):

        return point["lat"]

    return point.lat


def get_lon(point):

    if isinstance(point, dict):

        return point["lon"]

    return point.lon


def estimate_target_diameter(
    targets
):

    if len(targets) < 2:

        return 0

    max_distance = 0

    for i in range(len(targets)):

        for j in range(i + 1, len(targets)):

            d = distance_meters(

                get_lat(
                    targets[i]
                ),

                get_lon(
                    targets[i]
                ),

                get_lat(
                    targets[j]
                ),

                get_lon(
                    targets[j]
                )

            )

            max_distance = max(
                max_distance,
                d
            )

    return round(
        max_distance,
        2
    )