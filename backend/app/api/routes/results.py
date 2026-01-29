from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import ResultUpdateRequest
from app.api.utils import api_response
from app.models.detection import AnalysisResult
from app.models.event_type import EventType

router = APIRouter()


@router.patch("/results/{result_id}", summary="클립(분석 결과) 정보 수정")
async def update_result(
    result_id: int,
    payload: ResultUpdateRequest,
    db: Session = Depends(get_db),
):
    result = db.get(AnalysisResult, result_id)
    if not result:
        return api_response(404, False, "분석 결과를 찾을 수 없습니다.", None)

    if payload.event_type_id is not None:
        exists = db.query(EventType).filter(EventType.id == payload.event_type_id).one_or_none()
        if not exists:
            return api_response(400, False, "유효하지 않은 event_type_id 입니다.", None)
        result.event_type_id = payload.event_type_id

    for field in ["occurred_time", "license_plate_text", "clip_path", "license_plate_img"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(result, field, value)

    db.commit()
    db.refresh(result)

    data = {
        "result_id": result.id,
        "event_type_id": result.event_type_id,
        "occurred_time": result.occurred_time.isoformat() if result.occurred_time else None,
        "license_plate_text": result.license_plate_text,
        "clip_path": result.clip_path,
        "license_plate_img": result.license_plate_img,
    }
    return api_response(200, True, "클립 정보가 수정되었습니다.", data)


@router.delete("/results/{result_id}", summary="클립(분석 결과) 구간 삭제")
async def delete_result(result_id: int, db: Session = Depends(get_db)):
    result = db.get(AnalysisResult, result_id)
    if not result:
        return api_response(404, False, "분석 결과를 찾을 수 없습니다.", None)

    db.delete(result)
    db.commit()

    return api_response(
        200,
        True,
        "클립이 삭제되었습니다.",
        {"result_id": result_id, "deleted": True},
    )
