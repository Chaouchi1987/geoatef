import math


def generate_grid(
    lat,
    lon,
    radius_m,
    cell_size_m=None
):

    # ==========================
    # Fixed Resolution
    # ==========================

    if cell_size_m is None:
        cell_size_m = 2

    cells = []

    seen = set()

    lat_step = cell_size_m / 111320

    lon_step = (
        cell_size_m /
        (
            111320 *
            math.cos(
                math.radians(lat)
            )
        )
    )

    lat_radius = radius_m / 111320

    lon_radius = (
        radius_m /
        (
            111320 *
            math.cos(
                math.radians(lat)
            )
        )
    )

    lat_min = lat - lat_radius
    lat_max = lat + lat_radius

    lon_min = lon - lon_radius
    lon_max = lon + lon_radius

    # ==========================
    # Stable Grid Generation
    # ==========================

    lat_count = int(
        (lat_max - lat_min) / lat_step
    ) + 1

    lon_count = int(
        (lon_max - lon_min) / lon_step
    ) + 1

    for i in range(lat_count):

        current_lat = (
            lat_min +
            i * lat_step
        )

        for j in range(lon_count):

            current_lon = (
                lon_min +
                j * lon_step
            )

            dy = (
                current_lat - lat
            ) * 111320

            dx = (
                current_lon - lon
            ) * (
                111320 *
                math.cos(
                    math.radians(lat)
                )
            )

            distance = math.sqrt(
                dx ** 2 +
                dy ** 2
            )

            if distance <= radius_m:

                lat_round = round(
                    current_lat,
                    8
                )

                lon_round = round(
                    current_lon,
                    8
                )

                key = (
                    lat_round,
                    lon_round
                )

                if key not in seen:

                    seen.add(key)

                    cells.append({

                        "lat": lat_round,
                        "lon": lon_round

                    })

    print(
        "CELL SIZE =",
        cell_size_m,
        "m"
    )

    print(
        "UNIQUE CELLS =",
        len(cells)
    )

    return cells