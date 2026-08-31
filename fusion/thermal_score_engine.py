"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
def build_thermal_score(

    landsat_temp,

    aster_b10,
    aster_b11,
    aster_b12,
    aster_b13,
    aster_b14

):

    score = 0

    # -------------------
    # Landsat
    # -------------------

    if landsat_temp >= 20:

        score += 30

    # -------------------
    # ASTER
    # -------------------

    thermal_mean = (

        aster_b10 +
        aster_b11 +
        aster_b12 +
        aster_b13 +
        aster_b14

    ) / 5

    if thermal_mean > 1200:

        score += 40

    elif thermal_mean > 1000:

        score += 25

    # -------------------
    # Thermal Spread
    # -------------------

    spread = (

        max(
            aster_b10,
            aster_b11,
            aster_b12,
            aster_b13,
            aster_b14
        )

        -

        min(
            aster_b10,
            aster_b11,
            aster_b12,
            aster_b13,
            aster_b14
        )

    )

    if spread > 400:

        score += 30

    elif spread > 200:

        score += 15

    return round(
        min(score, 100),
        2
    )