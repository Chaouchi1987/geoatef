from dataclasses import dataclass


@dataclass
class EngineResult:

    score: float

    confidence: float = 0

    message: str = ""