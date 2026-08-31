from __future__ import annotations
import math
import pandas as pd
from backend.science.utm import wgs84_to_utm

def point_box_geojson(lat,lon,size_m=10.0):
    dlat=(size_m/2)/111320.0; dlon=(size_m/2)/(111320.0*max(math.cos(math.radians(lat)),.01))
    ring=[[lon-dlon,lat-dlat],[lon+dlon,lat-dlat],[lon+dlon,lat+dlat],[lon-dlon,lat+dlat],[lon-dlon,lat-dlat]]
    return {'type':'Feature','properties':{'size_m':size_m},'geometry':{'type':'Polygon','coordinates':[ring]}}

def _footprint(df,lat,lon,score,scale_m):
    import numpy as np
    R=6371000.0; lat0=math.radians(lat)
    x=np.radians(pd.to_numeric(df.lon,errors='coerce').to_numpy(float))*R*math.cos(lat0); y=np.radians(pd.to_numeric(df.lat,errors='coerce').to_numpy(float))*R
    x0=math.radians(lon)*R*math.cos(lat0); y0=math.radians(lat)*R
    d=np.hypot(x-x0,y-y0); s=pd.to_numeric(df.anomaly_score,errors='coerce').to_numpy(float)
    mask=(d<=max(20,scale_m*2.5))&(s>=max(score*.72,.55))
    if mask.sum()<2: return float(max(scale_m,10)),float(max(scale_m,10))
    arr=np.c_[x[mask]-x0,y[mask]-y0]
    cov=np.cov(arr.T) if len(arr)>=3 else np.eye(2); vals,vecs=np.linalg.eigh(cov); vecs=vecs[:,np.argsort(vals)[::-1]]; proj=arr@vecs
    return round(max(float(np.ptp(proj[:,0])),scale_m),1),round(max(float(np.ptp(proj[:,1])),scale_m),1)

def _num(row,key,default=0.0):
    try:
        v=float(row.get(key,default))
        return v if math.isfinite(v) else float(default)
    except (TypeError,ValueError):
        return float(default)


def _interpret(row,length,width):
    def val(key):
        try:
            v=float(row.get(key))
            return v if math.isfinite(v) else None
        except (TypeError,ValueError):
            return None
    def clamp(v): return max(0.0,min(1.0,v)) if v is not None else None
    a=clamp(val('anomaly_score')); g=clamp(val('geological_score')); ndvi=clamp(val('ndvi')); ndwi=clamp(val('ndwi')); built=clamp(val('built_surface_risk')); water=clamp(val('water_surface_risk')); human=clamp(val('human_surface_change_signal')); temporal=clamp(val('temporal_disturbance_score'))
    elong=max(length,width)/max(min(length,width),1)
    def wmean(parts):
        parts=[(v,w) for v,w in parts if v is not None and math.isfinite(v)]
        return sum(v*w for v,w in parts)/sum(w for _,w in parts) if parts else 0.0
    scores={
        # Vegetation absence is context, not disturbance evidence: bare soil is
        # common and must not become a target merely because NDVI is low.
        'surface_disturbance':wmean([(a,.45),(human,.35),(temporal,.20)]),
        # Water/moisture remains a separate surface-context hypothesis.
        'moisture_depression':wmean([(a,.40),(water,.40),(ndwi,.20)]),
        # Built-up probability is a surface artifact/context penalty, not a
        # positive mineral indicator.
        'mineral_alteration':wmean([(a,.60),(g,.40)]),
        'linear_structure':wmean([(a,.55),(min(elong/4,1),.25),(temporal,.20)]),
    }
    labels={
        'surface_disturbance':'Surface disturbance / anthropogenic-change hypothesis',
        'moisture_depression':'Moisture / surface-water anomaly hypothesis',
        'mineral_alteration':'Surface mineral / alteration signature hypothesis',
        'linear_structure':'Linear surface-feature hypothesis',
    }
    ordered=sorted(scores.items(),key=lambda kv:kv[1],reverse=True); best=ordered[0][0]
    return {'class':best,'label':labels[best],'fit_percent':round(scores[best]*100,1),'alternatives':[{'label':labels[k],'fit_percent':round(v*100,1)} for k,v in ordered[1:3]],'scientific_note':'Interpretation of observed surface signatures only. The fit is a hypothesis-fit score, not a probability and not evidence of a buried object or depth.'}

def distance_meters(lat1, lon1, lat2, lon2):
    r=6371000.0
    p1=math.radians(lat1); p2=math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return r*2*math.atan2(math.sqrt(a),math.sqrt(max(1-a,0)))

def build_targets(df,max_targets=3,scale_m=10.0,min_separation_m=30.0):
    work=df.dropna(subset=['lat','lon','anomaly_score']).sort_values('anomaly_score',ascending=False)
    out=[]
    for _,r in work.iterrows():
        lat=float(r.lat); lon=float(r.lon)
        if any(distance_meters(lat,lon,t['latitude'],t['longitude']) < min_separation_m for t in out):
            continue
        rank=len(out)+1
        lat=float(r.lat); lon=float(r.lon); length,width=_footprint(df,lat,lon,float(r.anomaly_score),scale_m); interp=_interpret(r,length,width); evidence=[]
        if float(r.get('isolation_forest_score',0) or 0)>=.7:evidence.append('Strong Isolation Forest deviation')
        if float(r.get('zscore_score',0) or 0)>=.7:evidence.append('Strong robust Z-score deviation')
        if float(r.get('geological_score',0) or 0)>=.7:evidence.append('Elevated spectral geological indicators')
        if float(r.get('consensus_score',0) or 0)>=.6:evidence.append('Multi-scale spatial consensus')
        if float(r.get('temporal_stability_score',0) or 0)>=.70:evidence.append('Temporal persistence of spectral proxies')
        if float(r.get('temporal_disturbance_score',0) or 0)>=.55:evidence.append('Historical surface spectral change')
        if float(r.get('human_surface_change_signal',0) or 0)>=.55:evidence.append('Independent land-cover change signal')
        if float(r.get('surface_artifact_risk',0) or 0)>=.55:evidence.append('High surface-context/artifact risk')
        if not evidence:evidence.append('Statistical anomaly signal; field verification required')
        out.append({'target_id':f'T{rank:02d}','rank':rank,'cell_id':str(r.get('cell_id')),'latitude':lat,'longitude':lon,'utm':wgs84_to_utm(lat,lon),'box_geojson':point_box_geojson(lat,lon,scale_m),'box_size_m':float(scale_m),'anomaly_score':float(r.anomaly_score),'strength_percent':round(float(r.anomaly_score)*100,1),'zscore_score':float(r.get('zscore_score',0) or 0),'isolation_forest_score':float(r.get('isolation_forest_score',0) or 0),'geological_score':float(r.get('geological_score',0) or 0),'consensus_score':float(r.get('consensus_score',0) or 0),'temporal_score':float(r.get('temporal_score',0) or 0),'temporal_disturbance_score':float(r.get('temporal_disturbance_score',0) or 0),'temporal_stability_score':float(r.get('temporal_stability_score',0) or 0),'thermal_score':float(r.get('thermal_score',0) or 0),'ndvi':_num(r,'ndvi'),'ndmi':_num(r,'ndmi'),'ndwi':_num(r,'ndwi'),'ndbi':_num(r,'ndbi'),'iron_oxide':_num(r,'iron_oxide'),'clay_ratio':_num(r,'clay_ratio'),'human_surface_change_signal':_num(r,'human_surface_change_signal'),'surface_artifact_risk':_num(r,'surface_artifact_risk'),'built_surface_risk':_num(r,'built_surface_risk'),'water_surface_risk':_num(r,'water_surface_risk'),'vegetation_mask_risk':_num(r,'vegetation_mask_risk'),'landcover_boundary_risk':_num(r,'landcover_boundary_risk'),'estimated_surface_length_m':length,'estimated_surface_width_m':width,'depth_estimate_m':None,'type_interpretation':interp,'evidence':evidence,'data_quality':{'source':'Earth Engine sampled data','synthetic':False}})
        if len(out) >= max_targets:
            break
    return out
