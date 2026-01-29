import logging
import sys
from pathlib import Path

from app.core.logging import InterceptHandler
from loguru import logger
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

API_PREFIX = "/api"
VERSION = "0.1.0"
DEBUG: bool = config("DEBUG", cast=bool, default=False)
MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)
SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret, default="")
DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./app.db")

PROJECT_NAME: str = config("PROJECT_NAME", default="backend")

# Optional integrations / paths
BASE_DIR = Path(__file__).resolve().parents[2]  # backend/ directory
STORAGE_BASE_DIR = BASE_DIR / "storage"
GCS_BUCKET_NAME: str = config("GCS_BUCKET_NAME", default="")
GPU_SSH_HOST: str = config("GPU_SSH_HOST", default="")
GPU_SSH_USER: str = config("GPU_SSH_USER", default="root")
GPU_SSH_PORT: int = config("GPU_SSH_PORT", cast=int, default=22)

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

ALLOWED_ORIGINS = config("ALLOWED_ORIGINS", default="http://localhost:5173")
