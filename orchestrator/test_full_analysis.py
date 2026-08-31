from backend.orchestrator.full_analysis_engine import (
    run_full_analysis
)

print(
    "\nFULL ANALYSIS TEST\n"
)

target = run_full_analysis(

    lat=35.367481,

    lon=7.755425,

    ai_score=100,

    geology_score=92.86,

    temporal_score=85.6,

    thermal_score=85,

    structural_score=20

)

print(target)