from enum import Enum

from sqlalchemy import Column, DateTime, Enum as PgEnum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db import Base

class ServiceStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (UniqueConstraint("video_id", name="uq_tasks_video"),)

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    status = Column(PgEnum(ServiceStatus, name="service_status"), nullable=False, default=ServiceStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    video = relationship("Video", backref="tasks", lazy="joined")
    results = relationship("AnalysisResult", back_populates="task", cascade="all, delete-orphan")
