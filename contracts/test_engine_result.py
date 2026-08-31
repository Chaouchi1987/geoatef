from backend.contracts.engine_result import (
    EngineResult
)

print(
    "\nENGINE RESULT TEST\n"
)

result = EngineResult(

    score=92,

    confidence=88,

    message="Strong anomaly"

)

print(result)