from backend.anomaly.grid_scan import (
    generate_grid
)

from backend.gee.grid_sampler import (
    sample_grid_features
)

from backend.gee.feature_matrix import (
    feature_collection_to_dataframe
)

from backend.fusion.landcover_engine import (
    classify_landcover
)

from backend.anomaly.anomaly_pipeline import (
    run_anomaly_pipeline
)

from backend.fusion.evidence_engine import (
    build_evidence_scores
)

from backend.orchestrator.target_zone_scan import (
    run_target_zone_scan
)

from backend.orchestrator.zone_validation import (
    validate_top_zones
)

from backend.orchestrator.multiscale_validation import (
    validate_multiscale
)

from backend.orchestrator.zone_intelligence import (
    build_zone_intelligence
)

from backend.core.safe_gee import (
    safe_get_info
)


def run_scan_v2(

    lat,
    lon,

    radius_m

):

    # -------------------------
    # GRID
    # -------------------------

    cells = generate_grid(

        lat=lat,

        lon=lon,

        radius_m=radius_m

    )

    print(
        "TOTAL CELLS =",
        len(cells)
    )

    # -------------------------
    # EE SAMPLE
    # -------------------------

    sample = sample_grid_features(
        cells
    )

    fc_info = safe_get_info(
        sample
    )

    if fc_info is None:

        return []

    # -------------------------
    # DATAFRAME
    # -------------------------

    df = feature_collection_to_dataframe(
        fc_info
    )

    df = classify_landcover(
        df
    )

    print(
        "DF SHAPE =",
        df.shape
    )

    # -------------------------
    # AI
    # -------------------------

    pipeline = run_anomaly_pipeline(
        df
    )

    # -------------------------
    # EVIDENCE
    # -------------------------

    evidence = build_evidence_scores(

        df,

        pipeline["iforest_labels"],

        pipeline["lof_labels"]

    )

    print(
        "EVIDENCE SHAPE =",
        evidence.shape
    )

    # -------------------------
    # TARGET ZONES
    # -------------------------

    zones = run_target_zone_scan(
        evidence
    )

    print(
        "TOTAL ZONES =",
        len(zones)
    )

    if len(zones) == 0:

        return []

    # -------------------------
    # ZONE VALIDATION
    # -------------------------

    validated = validate_top_zones(

        zones,

        top_n=min(
            3,
            len(zones)
        )

    )

    # -------------------------
    # MULTISCALE + FINAL INTELLIGENCE
    # -------------------------

    final_zones = []

    for zone in validated:

        zone = validate_multiscale(
            zone
        )

        zone = build_zone_intelligence(
            zone
        )

        final_zones.append(
            zone
        )

    print(
        "VALIDATED ZONES =",
        len(final_zones)
    )

    return final_zones