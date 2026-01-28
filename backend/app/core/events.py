from typing import Callable

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.exc import OperationalError

import app.models  # noqa: F401 ensures SQLAlchemy models are registered
from app.db import Base, engine


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        try:
            Base.metadata.create_all(bind=engine)
        except OperationalError:
            logger.exception("failed to initialize database")

    return start_app
