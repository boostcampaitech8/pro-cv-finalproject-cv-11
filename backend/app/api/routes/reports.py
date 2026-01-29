from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import ReportCreateRequest
from app.api.utils import api_response
from app.models.detection import AnalysisResult
from app.models.report import Report

router = APIRouter()


@router.post("/reports", summary="신고 전송", status_code=201)
async def create_report(
    payload: ReportCreateRequest,
    db: Session = Depends(get_db),
):
    result = db.get(AnalysisResult, payload.result_id)
    if not result:
        return api_response(400, False, "result_id를 찾을 수 없습니다.", None)

    report = Report(
        result_id=payload.result_id,
        title=payload.title,
        description=payload.description,
        occurred_time=payload.occurred_time,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    data = {
        "report_id": report.id,
        "result_id": report.result_id,
        "title": report.title,
        "description": report.description,
        "occurred_time": report.occurred_time.isoformat(),
        "report_created_at": report.created_at.isoformat() if report.created_at else None,
    }
    return api_response(201, True, "신고가 접수되었습니다.", data)


@router.get("/reports/{report_id}", summary="신고 조회")
async def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.get(Report, report_id)
    if not report:
        return api_response(404, False, "신고 정보를 찾을 수 없습니다.", None)

    data = {
        "report_id": report.id,
        "result_id": report.result_id,
        "title": report.title,
        "description": report.description,
        "occurred_time": report.occurred_time.isoformat(),
        "report_created_at": report.created_at.isoformat() if report.created_at else None,
    }
    return api_response(200, True, "신고 정보를 조회했습니다.", data)
