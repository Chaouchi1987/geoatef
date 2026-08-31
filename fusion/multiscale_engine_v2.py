import math


def distance_meters(
    lat1,
    lon1,
    lat2,
    lon2
):

    return (

        ((lat1 - lat2) * 111320) ** 2

        +

        ((lon1 - lon2) * 111320) ** 2

    ) ** 0.5


def build_multiscale_consensus(

    target_sets,

    threshold_m=50

):

    merged = []

    for targets in target_sets:

        for target in targets:

            found = False

            for item in merged:

                dist = distance_meters(

                    target["lat"],
                    target["lon"],

                    item["lat"],
                    item["lon"]

                )

                if dist <= threshold_m:

                    item["scores"].append(
                        target["score"]
                    )

                    item["count"] += 1

                    found = True

                    break

            if not found:

                merged.append({

                    "lat":
                        target["lat"],

                    "lon":
                        target["lon"],

                    "scores":
                        [target["score"]],

                    "count":
                        1

                })

    results = []

    for item in merged:

        results.append({

            "lat":
                item["lat"],

            "lon":
                item["lon"],

            "consensus":
                item["count"],

            "mean_score":
                round(
                    sum(item["scores"])
                    /
                    len(item["scores"]),
                    2
                )

        })

    results.sort(

        key=lambda x: (

            x["consensus"],
            x["mean_score"]

        ),

        reverse=True

    )

    return results