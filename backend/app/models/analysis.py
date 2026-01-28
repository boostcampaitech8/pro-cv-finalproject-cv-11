from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (UniqueConstraint("video_id", name="uq_tasks_video"),)

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    video = relationship("Video", backref="tasks", lazy="joined")
    results = relationship("AnalysisResult", back_populates="task", cascade="all, delete-orphan")
