from backend.contracts.target_model import (
    Target
)

print(
    "\nTARGET MODEL TEST\n"
)

target = Target(

    lat=35.367481,

    lon=7.755425

)

target.geology_score = 92.86

target.temporal_score = 85.6

target.ai_score = 100

print(
    target
)