from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel


class UserInfo(BaseModel):
    """사용자 정보"""
    phone: str
    share_content: str = "아니요"  # 예/아니요
    personal_info: Optional[str] = None
    llm_provider: str = "사용 안 함"  # 사용 안 함/OpenAI/Anthropic/Google
    llm_api_key: Optional[str] = None


class UploadResponse(BaseModel):
    """영상 업로드 응답"""
    task_id: UUID


class TaskStatusResponse(BaseModel):
    """작업 상태 조회 응답"""
    status: str
    progress: int
    current_step: str
    error_message: Optional[str] = None


class EventResponse(BaseModel):
    """이벤트 정보 응답"""
    event_id: UUID
    event_type: str  # 0번: 위반 이벤트 유형
    violation_type: str  # 1번: 자동차·교통 위반 신고 유형
    timestamp: str  # 영상 내 시간
    risk_level: str
    vehicle_number: str
    location: Optional[str] = None
    date: Optional[str] = None  # 파일명 파싱 실패 시 None
    time: Optional[str] = None  # 파일명 파싱 실패 시 None
    title: str
    content: str
    video_clip_path: Optional[str] = None
    images: dict  # key_frame, vehicle_crop, license_plate_crop


class TaskResultsResponse(BaseModel):
    """분석 결과 조회 응답"""
    task_id: UUID
    status: str
    events: List[EventResponse]

