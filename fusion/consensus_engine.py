import math


def distance_meters(
    lat1,
    lon1,
    lat2,
    lon2
):

    r = 6371000

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(
        lat2 - lat1
    )

    dl = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(dp / 2) ** 2
        +
        math.cos(p1)
        *
        math.cos(p2)
        *
        math.sin(dl / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return r * c


def build_consensus(
    targets_by_scale,
    tolerance_m=50
):

    consensus = []

    for scale_targets in targets_by_scale:

        for target in scale_targets:

            matched = False

            for item in consensus:

                d = distance_meters(
                    target["lat"],
                    target["lon"],
                    item["lat"],
                    item["lon"]
                )

                if d <= tolerance_m:

                    item["hits"] += 1

                    item["scores"].append(
                        target["score"]
                    )

                    matched = True

                    break

            if not matched:

                consensus.append({

                    "lat":
                        target["lat"],

                    "lon":
                        target["lon"],

                    "hits":
                        1,

                    "scores":
                        [target["score"]]

                })

    results = []

    for item in consensus:

        results.append({

            "lat":
                item["lat"],

            "lon":
                item["lon"],

            "consensus":
                item["hits"],

            "mean_score":
                round(
                    sum(item["scores"])
                    /
                    len(item["scores"]),
                    2
                )

        })

    results.sort(
        key=lambda x:
        (
            x["consensus"],
            x["mean_score"]
        ),
        reverse=True
    )

    return results