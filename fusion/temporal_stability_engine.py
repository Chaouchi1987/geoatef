import statistics


def stability_score(values):

    if len(values) <= 1:

        return 100.0

    mean_value = statistics.mean(
        values
    )

    if mean_value == 0:

        return 100.0

    stdev = statistics.pstdev(
        values
    )

    variation = (
        stdev
        /
        abs(mean_value)
    )

    score = 100 - (
        variation * 100
    )

    score = max(
        0,
        min(score, 100)
    )

    return round(
        score,
        2
    )


def build_temporal_stability(
    yearly_features
):

    iron_values = [
        x["iron"]
        for x in yearly_features
        if x["iron"] is not None
    ]

    clay_values = [
        x["clay"]
        for x in yearly_features
        if x["clay"] is not None
    ]

    ndvi_values = [
        x["ndvi"]
        for x in yearly_features
        if x["ndvi"] is not None
    ]

    iron_stability = stability_score(
        iron_values
    )

    clay_stability = stability_score(
        clay_values
    )

    ndvi_stability = stability_score(
        ndvi_values
    )

    temporal_score = round(

        (
            iron_stability
            +
            clay_stability
            +
            ndvi_stability
        )
        / 3,

        2

    )

    return {

        "iron_stability":
            iron_stability,

        "clay_stability":
            clay_stability,

        "ndvi_stability":
            ndvi_stability,

        "temporal_score":
            temporal_score

    }