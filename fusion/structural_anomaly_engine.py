import math


def calculate_angle(
    p1,
    p2
):

    if isinstance(p1, dict):

        lon1 = p1["lon"]
        lat1 = p1["lat"]

        lon2 = p2["lon"]
        lat2 = p2["lat"]

    else:

        lon1 = p1.lon
        lat1 = p1.lat

        lon2 = p2.lon
        lat2 = p2.lat

    dx = lon2 - lon1

    dy = lat2 - lat1

    return math.degrees(
        math.atan2(
            dy,
            dx
        )
    )


def detect_linear_patterns(
    targets,
    tolerance_deg=10
):

    if len(targets) < 3:

        return []

    patterns = []

    for i in range(len(targets) - 2):

        p1 = targets[i]

        p2 = targets[i + 1]

        p3 = targets[i + 2]

        a1 = calculate_angle(
            p1,
            p2
        )

        a2 = calculate_angle(
            p2,
            p3
        )

        if abs(a1 - a2) <= tolerance_deg:

            patterns.append({

                "type":
                    "linear",

                "angle":
                    round(a1, 2),

                "points":
                    [p1, p2, p3]

            })

    return patterns