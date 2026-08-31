from backend.orchestrator.thermal_pipeline import (
    run_thermal_pipeline
)

print(
    "\nTHERMAL PIPELINE TEST\n"
)

result = run_thermal_pipeline(

    lat=35.367481,

    lon=7.755425,

    start_date="2024-01-01",

    end_date="2024-12-31"

)

print(result)