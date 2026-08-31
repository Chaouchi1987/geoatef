from __future__ import annotations
import numpy as np
import pandas as pd

def robust_scale(v: pd.Series) -> pd.Series:
    v = pd.to_numeric(v, errors="coerce")
    med = v.median()
    mad = (v-med).abs().median()
    if not np.isfinite(mad) or mad == 0:
        std = v.std(ddof=0)
        if not np.isfinite(std) or std == 0:
            return pd.Series(np.zeros(len(v)), index=v.index)
        return ((v-v.mean())/std).abs()
    return (0.6745*(v-med)/mad).abs()

def neighborhood_consensus(df: pd.DataFrame, score_col="anomaly_score", radii_m=(10,20,50)) -> pd.DataFrame:
    df=df.copy()
    if not {"lat","lon",score_col}.issubset(df.columns):
        raise ValueError("lat, lon and anomaly_score are required for multi-scale consensus.")
    lat=np.radians(df["lat"].to_numpy(float))
    lon=np.radians(df["lon"].to_numpy(float))
    # Local equirectangular approximation is sufficient for small AOIs.
    R=6371000.0
    y=lat*R
    x=lon*R*np.cos(np.nanmean(lat))
    values=df[score_col].to_numpy(float)
    outputs=[]
    for i in range(len(df)):
        per=[]
        for r in radii_m:
            d=np.hypot(x-x[i], y-y[i])
            near=values[d<=r]
            per.append(float(np.nanmean(near)) if len(near) else float(values[i]))
        outputs.append(per)
    arr=np.asarray(outputs)
    df["consensus_mean"]=np.nanmean(arr,axis=1)
    df["consensus_std"]=np.nanstd(arr,axis=1)
    df["consensus_score"]=(df["consensus_mean"]*(1-df["consensus_std"].clip(0,1))).clip(0,1)
    return df
