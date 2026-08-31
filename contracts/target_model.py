from dataclasses import dataclass
from dataclasses import field


@dataclass
class Target:

    lat: float
    lon: float

    ai_score: float = 0

    geology_score: float = 0

    temporal_score: float = 0

    thermal_score: float = 0

    structural_score: float = 0

    intelligence_score: float = 0

    category: str = ""

    confidence: float = 0

    reasons: list = field(
        default_factory=list
    )