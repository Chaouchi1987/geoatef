from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from backend.core.store import RESULTS, RUNS
from backend.core.auth import current_user
from backend.reporting.report import build_report
from backend.reporting.pdf import make_pdf

router=APIRouter(prefix="/reports",tags=["reports"])

def _owned_result(analysis_id: str, request: Request):
    run=RUNS.get(analysis_id)
    if not run: raise HTTPException(404,"Analysis not found.")
    user=current_user(request)
    if run.get("user_id") != user["sub"]: raise HTTPException(403,"Analysis does not belong to the authenticated user.")
    if analysis_id not in RESULTS: raise HTTPException(409,"Scientific results are not ready.")
    return RESULTS[analysis_id]

@router.get("/{analysis_id}")
def report(analysis_id:str, request: Request):
    return build_report(_owned_result(analysis_id, request))

@router.get("/{analysis_id}/pdf")
def report_pdf(analysis_id:str, request: Request):
    result=_owned_result(analysis_id, request)
    pdf=make_pdf(build_report(result))
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition":f'attachment; filename="GeoAnomalyPro_{analysis_id}.pdf"'})
