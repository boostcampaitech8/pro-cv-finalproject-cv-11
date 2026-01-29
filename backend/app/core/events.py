from typing import Callable

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

import app.models  # noqa: F401 ensures SQLAlchemy models are registered
from app.db import Base, SessionLocal, engine
from app.models.event_type import EventType

DEFAULT_EVENT_TYPES = [
    (1, "불법 유턴"),
    (2, "신호 위반"),
    (3, "불법 주정차"),
    (4, "과속"),
]


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        try:
            Base.metadata.create_all(bind=engine)
            seed_default_event_types()
        except OperationalError:
            logger.exception("failed to initialize database")

    return start_app


def seed_default_event_types() -> None:
    """Ensure a minimal set of event types exists for demo/testing."""
    with SessionLocal() as db:  # type: Session
        for event_id, name in DEFAULT_EVENT_TYPES:
            exists = (
                db.query(EventType).filter(EventType.id == event_id).one_or_none()
            )
            if exists:
                continue
            db.add(EventType(id=event_id, event_name=name))
        db.commit()
