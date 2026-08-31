"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
import pandas as pd


def build_evidence_scores(
    df,
    iforest_labels,
    lof_labels
):

    results = []

    raw_scores = []

    # =========================
    # PASS 1
    # حساب الدرجات الخام
    # =========================

    for i in range(len(df)):

        row = df.iloc[i]

        score = 0

        # -------------------------
        # AI Evidence
        # -------------------------

        if iforest_labels[i] == -1:
            score += 30

        if lof_labels[i] == -1:
            score += 30

        # -------------------------
        # Iron
        # -------------------------

        score += min(
            row["iron"] * 5,
            12
        )

        # -------------------------
        # Clay
        # -------------------------

        score += min(
            row["clay"] * 5,
            12
        )

        # -------------------------
        # Built-up Penalty
        # -------------------------

        if row["ndbi"] > 0.15:
            score -= 15

        # -------------------------
        # Vegetation
        # -------------------------

        if row["ndvi"] > 0.50:

            score -= 10

        else:

            score += min(
                max(
                    1 - row["ndvi"],
                    0
                ) * 12,
                12
            )

        # -------------------------
        # Moisture Contrast
        # -------------------------

        score += min(
            abs(row["ndwi"]) * 12,
            12
        )

        # -------------------------
        # Landcover
        # -------------------------

        if "landcover" in row.index:

            if row["landcover"] == "Water":

                score -= 30

            elif row["landcover"] == "Built-up":

                score -= 25

            elif row["landcover"] == "Vegetation":

                score -= 10

            elif row["landcover"] == "Bare Soil":

                score += 5

        # -------------------------
        # Terrain
        # -------------------------

        if row["slope"] < 5:
            score += 6

        if row["elevation"] > 1000:
            score += 6

        # -------------------------
        # Road Risk Penalty
        # -------------------------

        if "road_risk" in row.index:

            score -= (
                row["road_risk"] * 0.50
            )

        # -------------------------
        # Building Risk Penalty
        # -------------------------

        if "building_risk" in row.index:

            score -= (
                row["building_risk"] * 0.70
            )

        # -------------------------
        # Agriculture Edge Penalty
        # -------------------------

        if "edge_risk" in row.index:

            score -= (
                row["edge_risk"] * 0.40
            )

        # -------------------------
        # Micro Target Bonus
        # -------------------------

        if row["slope"] < 2:
            score += 4

        if row["ndbi"] < 0:
            score += 3

        raw_scores.append(score)

    # =========================
    # NORMALIZATION
    # =========================
    # Fixed absolute bounds — ensures a cell with the same feature
    # values receives the same score regardless of scan area size.
    #
    # The previous relative normalization (batch min/max) caused scores
    # to shift every time the scan radius changed, making the same
    # target appear stronger or weaker at different scan sizes.
    #
    # Bounds from theoretical scoring range above:
    #   FIXED_MIN = -80  (worst case: all penalties, no AI flags)
    #   FIXED_MAX = 120  (best case: both AI flags + all bonuses)
    #   FIXED_RANGE = 200

    FIXED_MIN = -80
    FIXED_RANGE = 200

    # =========================
    # PASS 2
    # بناء النتائج النهائية
    # =========================

    for i in range(len(df)):

        row = df.iloc[i]

        raw_score = raw_scores[i]

        score = max(
            0.0,
            min(
                100.0,
                (raw_score - FIXED_MIN) / FIXED_RANGE * 100
            )
        )

        score = round(
            float(score),
            2
        )

        # -------------------------
        # Confidence
        # -------------------------

        confidence = 35

        if iforest_labels[i] == -1:
            confidence += 30

        if lof_labels[i] == -1:
            confidence += 30

        if (
            iforest_labels[i] == -1
            and
            lof_labels[i] == -1
        ):
            confidence += 5

        confidence = min(
            confidence,
            100
        )

        # -------------------------
        # Evidence Class
        # -------------------------

        if score >= 80:

            evidence = "Very Strong"

        elif score >= 60:

            evidence = "Strong"

        elif score >= 40:

            evidence = "Moderate"

        else:

            evidence = "Weak"

        results.append({

            "lat": row["lat"],
            "lon": row["lon"],

            "score": score,

            "confidence": round(
                confidence,
                2
            ),

            "evidence": evidence,

            # =====================
            # Landcover
            # =====================

            "landcover": row.get(
                "landcover",
                "Unknown"
            ),

            # =====================
            # Risk Layers
            # =====================

            "road_risk": row.get(
                "road_risk",
                0
            ),

            "building_risk": row.get(
                "building_risk",
                0
            ),

            "edge_risk": row.get(
                "edge_risk",
                0
            ),

            # =====================
            # Scientific Data
            # =====================

            "ndvi": row["ndvi"],
            "ndwi": row["ndwi"],
            "ndbi": row["ndbi"],

            "iron": row["iron"],
            "clay": row["clay"],

            "slope": row["slope"],
            "elevation": row["elevation"]

        })

    return pd.DataFrame(
        results
    )
