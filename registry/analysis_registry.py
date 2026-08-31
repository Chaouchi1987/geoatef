from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class AnalysisStage:
    id: str
    label: str
    order: int
    required: tuple[str, ...] = ()

STAGES = [
    AnalysisStage("acquisition","Data Acquisition",1),
    AnalysisStage("quality","Data Quality Control",2,("acquisition",)),
    AnalysisStage("landcover","Land-cover Filtering",3,("quality",)),
    AnalysisStage("spectral","Spectral Features",4,("landcover",)),
    AnalysisStage("sar","SAR Features",5,("quality",)),
    AnalysisStage("terrain","Terrain Features",6,("quality",)),
    AnalysisStage("temporal","Temporal Stability",7,("spectral",)),
    AnalysisStage("thermal","Thermal Analysis",8,("spectral",)),
    AnalysisStage("geology","Geological Intelligence",9,("spectral","terrain")),
    AnalysisStage("structural","Structural Analysis",10,("terrain",)),
    AnalysisStage("statistics","Statistical Anomaly Ensemble",11,("spectral","sar","terrain")),
    AnalysisStage("multiscale","Multi-scale Consensus",12,("statistics",)),
    AnalysisStage("clustering","Spatial Clustering",13,("multiscale",)),
    AnalysisStage("fusion","Evidence Fusion",14,("clustering","geology","temporal","thermal","structural")),
    AnalysisStage("ranking","Target Ranking",15,("fusion",)),
    AnalysisStage("report","Scientific Report",16,("ranking",)),
]
