from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.utils import api_response
from app.models.event_type import EventType

router = APIRouter()


@router.get("/event-types", summary="분석 이벤트 타입 목록 조회")
async def list_event_types(db: Session = Depends(get_db)):
    event_types = db.query(EventType).order_by(EventType.id).all()
    data = {
        "event_types": [
            {"event_type_id": et.id, "event_name": et.event_name} for et in event_types
        ]
    }
    return api_response(200, True, "이벤트 타입 목록을 조회했습니다.", data)
