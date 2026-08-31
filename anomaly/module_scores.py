def vegetation_score(report):

    score = (1 - report.ndvi) * 100

    return max(0, min(score, 100))


def moisture_score(report):

    score = abs(report.ndwi) * 100

    return max(0, min(score, 100))


def geological_score(report):

    score = (
        report.iron_oxide * 40 +
        report.clay_ratio * 30 +
        report.ndbi * 30
    )

    return max(0, min(score, 100))


def terrain_score(report):

    score = 0

    if report.slope_deg < 5:
        score += 50

    elif report.slope_deg < 15:
        score += 25

    if report.elevation_m > 1000:
        score += 50

    return min(score, 100)