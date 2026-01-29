from enum import Enum

from sqlalchemy import Column, DateTime, Enum as PgEnum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db import Base

class ServiceStatus(str, Enum):
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (UniqueConstraint("video_id", name="uq_tasks_video"),)

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        PgEnum(ServiceStatus, name="service_status"),
        nullable=False,
        default=ServiceStatus.UPLOADING,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    video = relationship("Video", backref="tasks", lazy="joined")
    results = relationship("AnalysisResult", back_populates="task", cascade="all, delete-orphan")
    event_requests = relationship(
        "TaskEvent",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class TaskEvent(Base):
    __tablename__ = "task_events"
    __table_args__ = (UniqueConstraint("task_id", "event_type_id", name="uq_task_events"),)

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    event_type_id = Column(Integer, ForeignKey("event_types.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    task = relationship("Task", back_populates="event_requests")
    event_type = relationship("EventType", lazy="joined")
