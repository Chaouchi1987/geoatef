from backend.anomaly.module_scores import (
    vegetation_score,
    moisture_score,
    geological_score,
    terrain_score
)

from backend.anomaly.anomaly_score import (
    calculate_anomaly_score
)


def build_frontend_result(report):

    anomaly = calculate_anomaly_score(report)

    return {

        "score": anomaly["anomaly_score"],

        "conf": 90,

        "dq": 95,

        "terrain": {
            "score": terrain_score(report),
            "slopeMean": report.slope_deg,
            "tpiMean": 0
        },

        "moisture": {
            "score": moisture_score(report),
            "anomaly": report.ndwi
        },

        "veg": {
            "score": vegetation_score(report),
            "stress": 1 - report.ndvi
        },

        "geo": {
            "score": geological_score(report),
            "ironOx": report.iron_oxide,
            "clay": report.clay_ratio
        },

        "risk_level": anomaly["risk_level"]
    }