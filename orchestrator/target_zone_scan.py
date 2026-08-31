from backend.fusion.cluster_engine import (
    build_clusters
)

from backend.orchestrator.target_zone_builder import (
    build_target_zone
)

from backend.fusion.target_zone_ranking import (
    rank_target_zones
)


def run_target_zone_scan(
    evidence_df
):

    # -------------------------
    # Cluster Engine
    # -------------------------

    clusters = build_clusters(
        evidence_df
    )

    # -------------------------
    # Build Zones
    # -------------------------

    zones = []

    for cluster in clusters:

        zone = build_target_zone(
            cluster
        )

        zones.append(
            zone
        )

    # -------------------------
    # Ranking
    # -------------------------

    ranked = rank_target_zones(
        zones
    )

    return ranked