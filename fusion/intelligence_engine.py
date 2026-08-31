def build_intelligence_score(

    geology_score,
    thermal_score,
    temporal_score,
    structural_score,
    ai_score,

    multiscale_score=0

):

    score = (

        geology_score * 0.25 +

        temporal_score * 0.25 +

        multiscale_score * 0.20 +

        ai_score * 0.15 +

        thermal_score * 0.05 +

        structural_score * 0.10

    )

    score = round(
        score,
        2
    )

    reasons = []

    if geology_score >= 80:

        reasons.append(
            "Strong geological anomaly"
        )

    if thermal_score >= 80:

        reasons.append(
            "Strong thermal contrast"
        )

    if temporal_score >= 80:

        reasons.append(
            "Long-term persistence"
        )

    if multiscale_score >= 90:

        reasons.append(
            "Stable across multiple scales"
        )

    if structural_score >= 60:

        reasons.append(
            "Possible geometric structure"
        )

    if ai_score >= 80:

        reasons.append(
            "AI anomaly consensus"
        )

    if score >= 85:

        category = (
            "High Priority Target"
        )

    elif score >= 70:

        category = (
            "Possible Human Activity"
        )

    elif score >= 50:

        category = (
            "Geological Interest"
        )

    elif score >= 30:

        category = (
            "Weak Anomaly"
        )

    else:

        category = (
            "Natural Background"
        )

    return {

        "intelligence_score":
            score,

        "category":
            category,

        "confidence":
            score,

        "reasons":
            reasons

    }