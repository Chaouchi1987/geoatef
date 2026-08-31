from dataclasses import dataclass
from dataclasses import field


@dataclass
class TargetZone:

    center_lat: float

    center_lon: float

    diameter_m: float = 0

    cells: int = 0

    mean_score: float = 0

    max_score: float = 0

    confidence: float = 0

    intelligence_score: float = 0

    temporal_score: float = 0

    thermal_score: float = 0

    multiscale_score: float = 0

    spatial_stability: float = 0

    structural_score: float = 0

    zone_points: list = field(
        default_factory=list
    )

    category: str = ""

    rank: int = 0

    reasons: list = field(
        default_factory=list
    )