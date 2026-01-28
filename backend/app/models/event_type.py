from sqlalchemy import Column, Integer, String

from app.db import Base


class EventType(Base):
    __tablename__ = "event_types"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(255), unique=True, nullable=False)
