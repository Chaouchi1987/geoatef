from backend.orchestrator.analysis_registry import (
    AVAILABLE_ENGINES
)

print(
    "\nENGINE REGISTRY\n"
)

for name, config in (

    AVAILABLE_ENGINES.items()

):

    print(

        name,

        "->",

        config

    )