import ee

from backend.gee.ee_init import (
    init_ee
)


def build_sentinel_composite(
    geometry,
    start_date="2025-01-01",
    end_date="2025-12-31"
):

    init_ee()

    image = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(geometry)
        .filterDate(
            start_date,
            end_date
        )
        .median()
    )

    ndvi = (
        image.normalizedDifference(
            ["B8", "B4"]
        )
        .rename("ndvi")
    )

    ndwi = (
        image.normalizedDifference(
            ["B3", "B8"]
        )
        .rename("ndwi")
    )

    ndbi = (
        image.normalizedDifference(
            ["B11", "B8"]
        )
        .rename("ndbi")
    )

    iron = (
        image.select("B4")
        .divide(
            image.select("B2")
        )
        .rename("iron")
    )

    clay = (
        image.select("B11")
        .divide(
            image.select("B12")
        )
        .rename("clay")
    )

    dem = (
        ee.Image(
            "USGS/SRTMGL1_003"
        )
        .rename("elevation")
    )

    slope = (
        ee.Terrain.slope(
            ee.Image(
                "USGS/SRTMGL1_003"
            )
        )
        .rename("slope")
    )

    return (
        ndvi
        .addBands(ndwi)
        .addBands(ndbi)
        .addBands(iron)
        .addBands(clay)
        .addBands(dem)
        .addBands(slope)
    )


def sample_grid_features(
    cells,
    start_date="2025-01-01",
    end_date="2025-12-31"
):

    init_ee()

    features = []

    for cell in cells:

        point = ee.Feature(
            ee.Geometry.Point(
                [
                    cell["lon"],
                    cell["lat"]
                ]
            )
        )

        features.append(
            point
        )

    fc = ee.FeatureCollection(
        features
    )

    geometry = fc.geometry()

    image = build_sentinel_composite(
        geometry,
        start_date,
        end_date
    )

    sampled = image.sampleRegions(
        collection=fc,
        scale=10,
        geometries=True
    )

    return sampled