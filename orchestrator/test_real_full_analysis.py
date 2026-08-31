from backend.orchestrator.full_analysis_engine_v2 import (
    run_full_analysis_v2
)

print(
    "\nREAL FULL ANALYSIS TEST\n"
)

target = run_full_analysis_v2(

    lat=35.367481,

    lon=7.755425,

    start_date="2024-01-01",

    end_date="2024-12-31",

    ai_score=100,

    geology_score=92.86,

    temporal_score=85.6,

    structural_score=20

)

print(target)