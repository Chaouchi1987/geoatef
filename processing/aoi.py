from __future__ import annotations
import math

def circle_geojson(lat: float, lon: float, radius_m: float, points: int = 72) -> dict:
    coords=[]
    lat_rad=math.radians(lat)
    for i in range(points+1):
        a=2*math.pi*i/points
        dx=radius_m*math.cos(a); dy=radius_m*math.sin(a)
        coords.append([lon+dx/(111320.0*max(math.cos(lat_rad),0.01)), lat+dy/111320.0])
    return {"type":"Feature","properties":{"radius_m":radius_m},"geometry":{"type":"Polygon","coordinates":[coords]}}

def square_geojson(lat: float, lon: float, radius_m: float) -> dict:
    lat_rad=math.radians(lat); dlat=radius_m/111320.0; dlon=radius_m/(111320.0*max(math.cos(lat_rad),0.01))
    ring=[[lon-dlon,lat-dlat],[lon+dlon,lat-dlat],[lon+dlon,lat+dlat],[lon-dlon,lat+dlat],[lon-dlon,lat-dlat]]
    return {"type":"Feature","properties":{"radius_m":radius_m},"geometry":{"type":"Polygon","coordinates":[ring]}}
