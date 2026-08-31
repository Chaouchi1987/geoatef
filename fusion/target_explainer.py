def explain_target(
    df,
    target_lat,
    target_lon
):

    nearest = df[
        (
            abs(df["lat"] - target_lat)
            < 0.0003
        )
        &
        (
            abs(df["lon"] - target_lon)
            < 0.0003
        )
    ]

    if len(nearest) == 0:

        return None

    row = nearest.iloc[0]

    return {

        "landcover":
            row.get(
                "landcover",
                None
            ),

        "ndvi":
            round(
                float(row["ndvi"]),
                4
            ),

        "ndwi":
            round(
                float(row["ndwi"]),
                4
            ),

        "ndbi":
            round(
                float(row["ndbi"]),
                4
            ),

        "iron":
            round(
                float(row["iron"]),
                4
            ),

        "clay":
            round(
                float(row["clay"]),
                4
            ),

        "elevation":
            round(
                float(row["elevation"]),
                2
            ),

        "slope":
            round(
                float(row["slope"]),
                2
            )

    }