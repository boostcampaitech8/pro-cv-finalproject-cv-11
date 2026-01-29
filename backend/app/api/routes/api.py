from fastapi import APIRouter

from app.api.routes import connect, event_types, reports, results, tasks, videos

router = APIRouter()
router.include_router(connect.router, tags=["connect"], prefix="/v1")
router.include_router(videos.router, tags=["videos"], prefix="/v1")
router.include_router(tasks.router, tags=["tasks"], prefix="/v1")
router.include_router(results.router, tags=["results"], prefix="/v1")
router.include_router(event_types.router, tags=["event-types"], prefix="/v1")
router.include_router(reports.router, tags=["reports"], prefix="/v1")
