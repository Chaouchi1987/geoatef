from backend.models.targeting import point_box_geojson

def test_target_box_is_polygon():
    g = point_box_geojson(35.0, 7.0, 10)
    assert g["geometry"]["type"] == "Polygon"
    ring = g["geometry"]["coordinates"][0]
    assert len(ring) == 5
    assert ring[0] == ring[-1]
