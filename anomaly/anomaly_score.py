from backend.anomaly.module_scores import (
    vegetation_score,
    moisture_score,
    geological_score,
    terrain_score
)


def calculate_anomaly_score(report):

    veg = vegetation_score(report)
    moist = moisture_score(report)
    geo = geological_score(report)
    terrain = terrain_score(report)

    score = (
        veg * 0.20 +
        moist * 0.15 +
        geo * 0.40 +
        terrain * 0.25
    )

    score = min(score, 100)

    if score < 35:
        risk = "Low"

    elif score < 70:
        risk = "Medium"

    else:
        risk = "High"

    return {
        "anomaly_score": round(score, 2),
        "risk_level": risk,

        "terrain": {
            "score": round(terrain, 2)
        },

        "moisture": {
            "score": round(moist, 2)
        },

        "veg": {
            "score": round(veg, 2)
        },

        "geo": {
            "score": round(geo, 2)
        }
    }