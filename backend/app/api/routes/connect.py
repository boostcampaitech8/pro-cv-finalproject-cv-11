from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db import SessionLocal

router = APIRouter()


@router.get("/connect_check", summary="Simple FE-BE connectivity check")
async def connect_check():
    """Returns 200 when backend is reachable."""
    return {"status": "ok", "detail": "backend reachable"}


@router.get("/db_check", summary="Quick DB connectivity check")
async def db_check():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok", "detail": "db reachable"}
    except Exception as exc:  # broad but fine for diagnostic endpoint
        return JSONResponse(
            status_code=503,
            content={"status": "fail", "detail": str(exc)},
        )
