from sklearn.neighbors import LocalOutlierFactor
import numpy as np


# ── Fixed parameters ──────────────────────────────────────────────────
# LOF.negative_outlier_factor_ returns scores where:
#   score ≈ -1.0  → inlier (normal density)
#   score << -1.0 → outlier (isolated from neighbors)
#
# OLD approach: contamination=0.05 forced exactly 5% to be outliers,
# and n_neighbors changed with batch size → both caused instability.
#
# NEW approach:
#   1. Fixed n_neighbors=5 (small enough to work on 10-cell batches,
#      large enough to be meaningful on 50-cell batches)
#   2. Z-score normalization within the batch, then fixed z-threshold.
#      This handles the fact that LOF scores are not directly comparable
#      across batch sizes — normalizing to standard deviations from the
#      batch mean makes the threshold stable regardless of radius.
#
# LOF_N_NEIGHBORS = 5:
#   Works for batches as small as 6 cells (n_neighbors < n_samples).
#
# LOF_Z_THRESHOLD = 1.8:
#   A cell must be 1.8 standard deviations more isolated than the
#   batch average to be flagged. Conservative — avoids false positives
#   while catching genuinely isolated cells.

LOF_N_NEIGHBORS = 5
LOF_Z_THRESHOLD = 1.8


def run_lof(df):

    features = df.drop(
        columns=["lat", "lon"]
    )

    n_samples = len(features)

    # LOF requires at least 2 samples
    if n_samples < 2:
        return {
            "labels": np.array([1] * n_samples),
            "scores": np.array([-1.0] * n_samples)
        }

    n_neighbors = min(
        LOF_N_NEIGHBORS,
        n_samples - 1
    )

    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination="auto"  # disables forced-percentage labeling
    )

    lof.fit_predict(features)

    raw_scores = lof.negative_outlier_factor_

    # Z-score normalization: makes threshold stable across batch sizes
    mean = np.mean(raw_scores)
    std = np.std(raw_scores)

    if std < 1e-6:
        # All cells have identical density — no outliers
        z_scores = np.zeros(len(raw_scores))
    else:
        z_scores = (raw_scores - mean) / std

    # Flag cells more than LOF_Z_THRESHOLD std below the batch mean
    labels = np.where(z_scores < -LOF_Z_THRESHOLD, -1, 1)

    return {
        "labels": labels,
        "scores": raw_scores
    }
