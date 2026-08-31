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


def rank_targets(
    evidence_df,
    top_n=5,
    min_distance=150
):

    ranked = evidence_df.sort_values(
        "score",
        ascending=False
    )

    targets = []

    for _, row in ranked.iterrows():

        keep = True

        for t in targets:

            d = distance_meters(
                row["lat"],
                row["lon"],
                t["lat"],
                t["lon"]
            )

            if d < min_distance:

                keep = False
                break

        if keep:

            targets.append({

                "lat": row["lat"],
                "lon": row["lon"],

                "score": row["score"],

                "confidence":
                    row["confidence"],

                "evidence":
                    row["evidence"]

            })

        if len(targets) >= top_n:
            break

    return targets