from __future__ import annotations
import math

def _deltas(lat: float, radius_m: float):
    dlat=float(radius_m)/111320.0
    dlon=float(radius_m)/(111320.0*max(math.cos(math.radians(float(lat))),0.01))
    return dlat,dlon

def make_square_geometry(lat: float, lon: float, radius_m: float):
    import ee
    dlat,dlon=_deltas(lat,radius_m)
    return ee.Geometry.Rectangle([float(lon)-dlon,float(lat)-dlat,float(lon)+dlon,float(lat)+dlat])

def make_circle_geometry(lat: float, lon: float, radius_m: float):
    import ee
    return ee.Geometry.Point([float(lon),float(lat)]).buffer(float(radius_m))

def make_aoi_geometry(lat: float, lon: float, radius_m: float, geometry_type: str = "circle"):
    if geometry_type == "square": return make_square_geometry(lat,lon,radius_m)
    return make_circle_geometry(lat,lon,radius_m)

def make_aoi_bbox(lat: float, lon: float, radius_m: float) -> list[float]:
    dlat,dlon=_deltas(lat,radius_m)
    return [float(lon)-dlon,float(lat)-dlat,float(lon)+dlon,float(lat)+dlat]

def make_point_grid(geometry, scale_m: int):
    import ee
    scale=int(scale_m)
    if scale<1: raise ValueError("Grid scale must be positive.")
    cells=geometry.coveringGrid(ee.Projection("EPSG:4326").atScale(scale))
    def decorate(feature):
        centroid=feature.geometry().centroid(scale).coordinates()
        lon=ee.Number(centroid.get(0)); lat=ee.Number(centroid.get(1))
        cell_id=ee.String("cell_").cat(lon.format("%.9f")).cat("_").cat(lat.format("%.9f"))
        point = ee.Geometry.Point([lon, lat])
        inside = geometry.contains(point, ee.ErrorMargin(max(1, scale)))
        return ee.Feature(point).set({"cell_id":cell_id,"grid_lon":lon,"grid_lat":lat,"grid_scale_m":scale,"inside_aoi":inside})
    return ee.FeatureCollection(cells.map(decorate)).filter(ee.Filter.eq("inside_aoi", True))
