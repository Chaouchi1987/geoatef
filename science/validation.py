from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

@dataclass
class FieldValidation:
    target_id: str
    outcome: Literal["confirmed","not_confirmed","natural","anthropogenic","unknown"]
    notes: str = ""
    validator: str = ""

def validation_metrics(records: list[FieldValidation]) -> dict:
    if not records:
        return {"n":0,"precision":None,"recall":None,"note":"No field-validation records available."}
    # Conservative metrics: only confirmed vs not_confirmed are treated as binary.
    binary=[r for r in records if r.outcome in ("confirmed","not_confirmed")]
    if not binary:
        return {"n":len(records),"precision":None,"recall":None,"note":"Insufficient binary field-validation records."}
    confirmed=sum(r.outcome=="confirmed" for r in binary)
    return {
        "n":len(binary),
        "confirmed":confirmed,
        "not_confirmed":len(binary)-confirmed,
        "note":"Metrics are intentionally withheld until predictions and sampling design are paired with ground truth."
    }
