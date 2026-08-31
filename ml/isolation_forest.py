from sklearn.ensemble import IsolationForest
import numpy as np


# ── Fixed threshold ───────────────────────────────────────────────────
# IsolationForest.decision_function() returns a score where:
#   score > 0  → inlier (normal)
#   score < 0  → anomalous (more negative = more anomalous)
#
# OLD approach: contamination=0.05 forced exactly 5% to be outliers,
# so the number of flagged cells changed with batch size → unstable.
#
# NEW approach: any cell whose score drops below THRESHOLD is flagged,
# regardless of how many other cells are in the batch.
# This makes the label for a given cell depend only on its OWN features,
# not on how many neighbors were sampled with it.
#
# THRESHOLD = -0.05:
#   - Cells clearly inside the normal distribution score > 0
#   - Cells on the boundary score ≈ 0
#   - Genuine outliers score well below -0.05
#   - Conservative: avoids flagging borderline cells
IF_THRESHOLD = -0.05


def run_isolation_forest(df):

    features = df.drop(
        columns=["lat", "lon"]
    )

    model = IsolationForest(
        n_estimators=200,
        contamination="auto",  # disables forced-percentage labeling
        random_state=42
    )

    model.fit(features)

    scores = model.decision_function(features)

    # Apply fixed threshold instead of contamination-based predict()
    labels = np.where(scores < IF_THRESHOLD, -1, 1)

    return {
        "scores": scores,
        "labels": labels
    }
