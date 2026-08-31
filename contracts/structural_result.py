from dataclasses import dataclass
from dataclasses import field


@dataclass
class StructuralResult:

    structural_score: float = 0

    pattern_score: float = 0

    geometry_score: float = 0

    diameter_m: float = 0

    patterns: list = field(
        default_factory=list
    )