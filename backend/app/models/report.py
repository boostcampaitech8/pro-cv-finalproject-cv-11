from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("analysis_results.id", ondelete="SET NULL"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    occurred_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    result = relationship("AnalysisResult", lazy="joined", backref="reports")
