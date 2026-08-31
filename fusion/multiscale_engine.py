from backend.anomaly.grid_scan import (
    generate_grid
)

from backend.gee.grid_sampler import (
    sample_grid_features
)

from backend.gee.feature_matrix import (
    feature_collection_to_dataframe
)

from backend.anomaly.anomaly_pipeline import (
    run_anomaly_pipeline
)

from backend.fusion.evidence_engine import (
    build_evidence_scores
)

from backend.fusion.target_ranking import (
    rank_targets
)

from backend.fusion.consensus_engine import (
    build_consensus
)


def run_multiscale_analysis(
    lat,
    lon
):

    radii = [
        50,
        100,
        200,
        300,
        500
    ]

    targets_by_scale = []

    for radius in radii:

        print(
            "MULTISCALE RADIUS =",
            radius
        )

        cells = generate_grid(
            lat=lat,
            lon=lon,
            radius_m=radius
        )

        sample = sample_grid_features(
            cells
        )

        fc_info = sample.getInfo()

        df = feature_collection_to_dataframe(
            fc_info
        )

        if len(df) == 0:
            continue

        pipeline = run_anomaly_pipeline(
            df
        )

        evidence = build_evidence_scores(
            df,
            pipeline["iforest_labels"],
            pipeline["lof_labels"]
        )

        targets = rank_targets(
            evidence,
            top_n=5,
            min_distance=150
        )

        targets = [
            t
            for t in targets
            if t["score"] >= 50
        ]

        print(
            "TARGETS FOUND =",
            len(targets)
        )

        targets_by_scale.append(
            targets
        )

    consensus = build_consensus(
        targets_by_scale
    )

    return consensus