from backend.gee.grid_sampler import (
    sample_grid_features
)

from backend.gee.feature_matrix import (
    feature_collection_to_dataframe
)


def run_feature_pipeline(

    cells,

    start_date="2025-01-01",

    end_date="2025-12-31"

):

    sampled = sample_grid_features(

        cells=cells,

        start_date=start_date,

        end_date=end_date

    )

    fc_info = sampled.getInfo()

    df = feature_collection_to_dataframe(
        fc_info
    )

    return df