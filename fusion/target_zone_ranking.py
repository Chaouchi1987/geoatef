def rank_target_zones(
    zones
):

    ranked = sorted(

        zones,

        key=lambda z: (

            z.confidence,

            z.max_score,

            z.cells

        ),

        reverse=True

    )

    for i, zone in enumerate(
        ranked,
        start=1
    ):

        zone.rank = i

    return ranked