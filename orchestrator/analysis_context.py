from dataclasses import dataclass


@dataclass
class AnalysisContext:

    df: object = None

    thermal: object = None

    temporal: object = None

    geology: object = None

    ai: object = None

    target: object = None