from __future__ import annotations
import math

def wgs84_to_utm(lat: float, lon: float) -> dict:
    a=6378137.0; ecc_sq=0.0066943799901413165; k0=0.9996
    lat_r=math.radians(lat); lon_r=math.radians(lon)
    zone=int((lon+180)/6)+1; lon0=math.radians((zone-1)*6-180+3)
    ep=ecc_sq/(1-ecc_sq); N=a/math.sqrt(1-ecc_sq*math.sin(lat_r)**2)
    T=math.tan(lat_r)**2; C=ep*math.cos(lat_r)**2; A=math.cos(lat_r)*(lon_r-lon0)
    M=a*((1-ecc_sq/4-3*ecc_sq**2/64-5*ecc_sq**3/256)*lat_r-(3*ecc_sq/8+3*ecc_sq**2/32+45*ecc_sq**3/1024)*math.sin(2*lat_r)+(15*ecc_sq**2/256+45*ecc_sq**3/1024)*math.sin(4*lat_r)-(35*ecc_sq**3/3072)*math.sin(6*lat_r))
    E=k0*N*(A+(1-T+C)*A**3/6+(5-18*T+T*T+72*C-58*ep)*A**5/120)+500000
    Y=k0*(M+N*math.tan(lat_r)*(A*A/2+(5-T+9*C+4*C*C)*A**4/24+(61-58*T+T*T+600*C-330*ep)*A**6/720))
    hemi='N' if lat>=0 else 'S'
    if lat<0: Y+=10000000
    return {'zone':zone,'hemisphere':hemi,'epsg':32600+zone if lat>=0 else 32700+zone,'easting_m':E,'northing_m':Y,'label':f'UTM {zone}{hemi} · E {E:.2f} m · N {Y:.2f} m'}
