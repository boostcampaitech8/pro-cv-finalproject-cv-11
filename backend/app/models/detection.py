from enum import Enum

from sqlalchemy import Column, DateTime, Enum as PgEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class ServiceStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    event_type_id = Column(Integer, ForeignKey("event_types.id", ondelete="CASCADE"), nullable=False)
    status = Column(PgEnum(ServiceStatus, name="service_status"), nullable=False, default=ServiceStatus.PENDING)
    clip_path = Column(String(512), nullable=True)
    occurred_time = Column(DateTime(timezone=True), nullable=True)
    license_plate_img = Column(String(512), nullable=True)
    license_plate_text = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    task = relationship("Task", back_populates="results")
    event_type = relationship("EventType", lazy="joined")
