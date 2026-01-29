from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StartTaskRequest(BaseModel):
    event_type_ids: List[int] = Field(default_factory=list, description="IDs of event types to analyze")


class ResultUpdateRequest(BaseModel):
    event_type_id: Optional[int] = None
    occurred_time: Optional[datetime] = None
    license_plate_text: Optional[str] = None
    clip_path: Optional[str] = None
    license_plate_img: Optional[str] = None


class ReportCreateRequest(BaseModel):
    result_id: int
    title: str
    description: str
    occurred_time: datetime
