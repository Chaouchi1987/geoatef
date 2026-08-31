from sklearn.cluster import DBSCAN

import numpy as np

from math import radians
from math import cos


def build_clusters(
    evidence_df,
    min_score=80,
    eps_meters=25,
    min_samples=2
):

    strong = evidence_df[
        evidence_df["score"] >= min_score
    ].copy()

    print(
        "STRONG CELLS =",
        len(strong)
    )

    if len(strong) > 0:

        print(
            strong[
                [
                    "lat",
                    "lon",
                    "score"
                ]
            ]
        )

    if len(strong) == 0:
        return []

    lat0 = strong["lat"].mean()

    strong["x"] = (
        strong["lon"]
        * 111320
        * cos(radians(lat0))
    )

    strong["y"] = (
        strong["lat"]
        * 111320
    )

    coords = strong[
        ["x", "y"]
    ].values

    model = DBSCAN(
        eps=eps_meters,
        min_samples=min_samples
    )

    labels = model.fit_predict(
        coords
    )

    strong["cluster"] = labels

    print(
        "CLUSTER LABELS =",
        list(labels)
    )

    clusters = []

    for cid in strong["cluster"].unique():

        if cid == -1:
            continue

        c = strong[
            strong["cluster"] == cid
        ]

        x_span = (
            c["x"].max()
            -
            c["x"].min()
        )

        y_span = (
            c["y"].max()
            -
            c["y"].min()
        )

        diameter = float(
            np.sqrt(
                x_span**2 +
                y_span**2
            )
        )

        clusters.append({

            "cluster_id":
                int(cid),

            "lat":
                float(
                    c["lat"].mean()
                ),

            "lon":
                float(
                    c["lon"].mean()
                ),

            # =====================
            # KEEP FULL CELL DATA
            # =====================

            "points":
                c.to_dict(
                    "records"
                ),

            "cells":
                int(len(c)),

            "mean_score":
                round(
                    float(
                        c["score"].mean()
                    ),
                    2
                ),

            "max_score":
                round(
                    float(
                        c["score"].max()
                    ),
                    2
                ),

            "diameter_m":
                round(
                    diameter,
                    2
                )

        })

    clusters.sort(
        key=lambda x:
        (
            x["mean_score"],
            x["cells"]
        ),
        reverse=True
    )

    print(
        "TOTAL CLUSTERS =",
        len(clusters)
    )

    if len(clusters) > 0:

        print(
            "BEST CLUSTER =",
            clusters[0]
        )

    return clusters