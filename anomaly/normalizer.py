import pandas as pd


# ==========================================================
# Fixed Physical Normalization
# Uses scientific ranges instead of batch MinMaxScaler
# ==========================================================

FEATURE_RANGES = {

    "ndvi": (-1.0, 1.0),

    "ndwi": (-1.0, 1.0),

    "ndbi": (-1.0, 1.0),

    "iron": (0.0, 2.0),

    "clay": (0.0, 2.0),

    "slope": (0.0, 90.0),

    "elevation": (-500.0, 9000.0)

}


def normalize_value(value, minimum, maximum):

    value = max(minimum, min(value, maximum))

    return (value - minimum) / (maximum - minimum)


def normalize_features(feature_list):

    df = pd.DataFrame(feature_list)

    coords = df[["lat", "lon"]].copy()

    values = df.select_dtypes(
        include=["number"]
    ).drop(
        columns=["lat", "lon"],
        errors="ignore"
    )

    normalized = pd.DataFrame()

    for column in values.columns:

        if column in FEATURE_RANGES:

            minimum, maximum = FEATURE_RANGES[column]

            normalized[column] = values[column].apply(
                lambda x: normalize_value(
                    x,
                    minimum,
                    maximum
                )
            )

        else:

            # أي Feature جديدة لا نكسر المشروع
            normalized[column] = values[column]

    result = pd.concat(

        [
            coords,
            normalized
        ],

        axis=1

    )

    return result