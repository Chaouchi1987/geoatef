import numpy as np


def compute_thg(grid):

    dy, dx = np.gradient(grid)

    thg = np.sqrt(
        dx**2 +
        dy**2
    )

    return thg


def compute_tdx(grid):

    dy, dx = np.gradient(grid)

    horizontal = np.sqrt(
        dx**2 +
        dy**2
    )

    dzz = np.gradient(
        np.gradient(grid, axis=0),
        axis=0
    )

    eps = 1e-10

    tdx = np.arctan(
        horizontal /
        (
            np.abs(dzz) + eps
        )
    )

    return tdx


def structural_score(grid):

    thg = compute_thg(grid)

    tdx = compute_tdx(grid)

    thg_mean = np.mean(thg)

    tdx_mean = np.mean(tdx)

    raw_score = (
        thg_mean * 50 +
        tdx_mean * 50
    )

    score = min(
        max(raw_score, 0),
        100
    )

    return round(
        float(score),
        2
    )