import pandas as pd


def feature_collection_to_dataframe(
    fc_info
):

    rows = []

    for feature in fc_info["features"]:

        props = feature["properties"]

        lon = feature["geometry"]["coordinates"][0]
        lat = feature["geometry"]["coordinates"][1]

        rows.append({

            "lat": lat,
            "lon": lon,

            "ndvi": props["ndvi"],
            "ndwi": props["ndwi"],
            "ndbi": props["ndbi"],

            "iron": props["iron"],
            "clay": props["clay"],

            "elevation": props["elevation"],
            "slope": props["slope"]

        })

    df = pd.DataFrame(rows)

    before = len(df)

    df = df.drop_duplicates(
        subset=[
            "lat",
            "lon"
        ]
    )

    after = len(df)

    print(
        "DEDUP:",
        before,
        "->",
        after
    )

    # =====================================
    # Road Risk
    # =====================================

    df["road_risk"] = 0

    road_mask = (

        (df["ndvi"] < 0.12)

        &

        (df["ndbi"] > 0.08)

        &

        (df["slope"] < 2)

    )

    df.loc[
        road_mask,
        "road_risk"
    ] = 60

    # =====================================
    # Building Risk
    # =====================================

    df["building_risk"] = 0

    building_mask = (

        (df["ndbi"] > 0.12)

        &

        (df["ndvi"] < 0.25)

    )

    df.loc[
        building_mask,
        "building_risk"
    ] = 80

    # =====================================
    # Agriculture Edge Risk
    # =====================================

    df["edge_risk"] = 0

    edge_mask = (

        (df["ndvi"] > 0.25)

        &

        (df["ndvi"] < 0.45)

        &

        (abs(df["ndwi"]) > 0.35)

    )

    df.loc[
        edge_mask,
        "edge_risk"
    ] = 30

    # =====================================
    # Statistics
    # =====================================

    road_cells = len(
        df[
            df["road_risk"] > 0
        ]
    )

    building_cells = len(
        df[
            df["building_risk"] > 0
        ]
    )

    edge_cells = len(
        df[
            df["edge_risk"] > 0
        ]
    )

    print(
        "ROAD CELLS =",
        road_cells
    )

    print(
        "BUILDING CELLS =",
        building_cells
    )

    print(
        "EDGE CELLS =",
        edge_cells
    )

    return df