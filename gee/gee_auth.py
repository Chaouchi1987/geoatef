import ee

from backend.gee.ee_init import (
    init_ee
)


def test_connection():

    init_ee()

    point = ee.Geometry.Point(
        [7.760, 35.376]
    )

    return point.getInfo()