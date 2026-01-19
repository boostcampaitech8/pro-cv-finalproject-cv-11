import datetime
from uuid import UUID
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine
from config import config


class Task(SQLModel, table=True):
    """작업 상태 관리 테이블"""
    id: UUID = Field(default=None, primary_key=True)
    status: str = Field(default="pending")  # pending, processing, completed, failed
    progress: int = Field(default=0)  # 0-100
    current_step: str = Field(default="대기 중")
    video_path: str  # 상대 경로
    user_info: str  # JSON 문자열
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    error_message: Optional[str] = None


class Event(SQLModel, table=True):
    """검출된 이벤트 테이블"""
    id: UUID = Field(default=None, primary_key=True)
    task_id: UUID = Field(foreign_key="task.id")
    event_type: str  # 0번: 위반 이벤트 유형
    violation_type: str  # 1번: 자동차·교통 위반 신고 유형
    timestamp: str  # 영상 내 시간 (예: "00:01:23")
    risk_level: str  # 높음, 중간, 낮음
    vehicle_number: str  # 차량 번호
    location: Optional[str] = None  # GPS 정보 (나중에 구현)
    date: Optional[str] = None  # 발생 일자 (파일명 파싱 실패 시 None)
    time: Optional[str] = None  # 발생 시각 (파일명 파싱 실패 시 None)
    title: str  # 제목
    content: str  # 신고 내용
    video_clip_path: Optional[str] = None  # 상대 경로
    key_frame_path: Optional[str] = None  # 상대 경로
    vehicle_crop_path: Optional[str] = None  # 상대 경로
    license_crop_path: Optional[str] = None  # 상대 경로
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


# 데이터베이스 엔진 생성
engine = create_engine(config.db_url, echo=False)

