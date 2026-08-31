from backend.anomaly.normalizer import normalize_features

from backend.ml.pca_engine import run_pca

from backend.ml.isolation_forest import (
    run_isolation_forest
)

from backend.ml.lof_engine import (
    run_lof
)


def run_anomaly_pipeline(df):

    # ----------------------------------
    # Numeric Features Only
    # ----------------------------------

    ml_df = df.select_dtypes(
        include=["number"]
    )

    normalized = normalize_features(
        ml_df.to_dict("records")
    )

    pca_result = run_pca(
        normalized
    )

    iforest_result = run_isolation_forest(
        normalized
    )

    lof_result = run_lof(
        normalized
    )

    return {

        "normalized": normalized,

        "pca_variance":
            pca_result["variance"],

        "iforest_labels":
            iforest_result["labels"],

        "lof_labels":
            iforest_result["labels"],

       

    }