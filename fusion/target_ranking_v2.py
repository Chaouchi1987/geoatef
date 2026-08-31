def rank_targets_v2(
    targets
):

    ranked = sorted(

        targets,

        key=lambda t: (

            t.intelligence_score,

            t.temporal_score,

            t.geology_score

        ),

        reverse=True

    )

    return ranked