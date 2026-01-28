from fastapi import APIRouter

from app.api.routes import connect

router = APIRouter()
router.include_router(connect.router, tags=["connect"], prefix="/v1")
