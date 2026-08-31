"""LEGACY: compatibility module; production API does not use this path.
Do not interpret its scores as calibrated probabilities.
"""
import pandas as pd


def build_final_score(
    ai_score,
    geology_score,
    ai_weight=0.70,
    geology_weight=0.30
):

    final_score = (

        ai_score * ai_weight

        +

        geology_score * geology_weight

    )

    return round(
        float(final_score),
        2
    )


def build_final_scores_dataframe(
    df
):

    result = df.copy()

    final_scores = []

    for _, row in result.iterrows():

        score = build_final_score(

            ai_score=row["score"],

            geology_score=row["geology_score"]

        )

        final_scores.append(score)

    result["final_score"] = final_scores

    return result