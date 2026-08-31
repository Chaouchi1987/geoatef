from __future__ import annotations
import pandas as pd


def classify_landcover(df: pd.DataFrame):
    """Classify only from independent Dynamic World probabilities when present.

    The old NDVI/NDWI/NDBI threshold classifier is intentionally removed because
    those indices alone cannot reliably distinguish vegetation, bare soil and
    built-up surfaces.
    """
    result=df.copy()
    classes=[]
    for _,row in result.iterrows():
        probs={k:float(row.get(k,0) or 0) for k in ("water","trees","crops","built","bare")}
        if max(probs.values(),default=0) < .45:
            classes.append("Uncertain")
        else:
            classes.append(max(probs,key=probs.get).replace("built","Built-up").replace("trees","Tree cover").replace("crops","Cropland").replace("water","Water").replace("bare","Bare / sparse"))
    result["landcover"]=classes
    result["landcover_source"]="Dynamic World V1 probabilities" if any(c in result.columns for c in ("water","trees","crops","built","bare")) else "Unavailable"
    return result
