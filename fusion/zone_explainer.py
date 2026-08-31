def explain_zone(
    zone
):

    reasons = []

    if zone.mean_score >= 90:

        reasons.append(
            "Very high anomaly concentration"
        )

    elif zone.mean_score >= 80:

        reasons.append(
            "High anomaly concentration"
        )

    if zone.cells >= 4:

        reasons.append(
            "Multiple supporting cells"
        )

    if zone.diameter_m <= 50:

        reasons.append(
            "Compact anomaly footprint"
        )

    return reasons