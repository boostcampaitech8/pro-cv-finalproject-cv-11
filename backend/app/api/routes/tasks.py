import time
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import StartTaskRequest
from app.api.utils import api_response
from app.core.config import GPU_SSH_HOST, GPU_SSH_PORT, GPU_SSH_USER
from app.db import SessionLocal
from app.models.analysis import ServiceStatus, Task, TaskEvent
from app.models.detection import AnalysisResult
from app.models.event_type import EventType
from app.services.storage import build_example_clip_path, build_example_plate_path

router = APIRouter()

SIMULATED_DELAY_SECONDS = 1.0


@router.post("/tasks/{task_id}/start", summary="인자 체크 및 분석 시작 (비동기 시작)", status_code=202)
async def start_task(
    task_id: int,
    payload: StartTaskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)
    if not task:
        return api_response(404, False, "작업(task)을 찾을 수 없습니다.", None)

    if task.status == ServiceStatus.PROCESSING:
        return api_response(
            409,
            False,
            "이미 PROCESSING 상태입니다.",
            {"task_id": task.id, "status": task.status.value},
        )
    if task.status == ServiceStatus.COMPLETED:
        return api_response(
            409,
            False,
            "이미 COMPLETED 상태입니다. 새 영상으로 다시 시도하세요.",
            {"task_id": task.id, "status": task.status.value},
        )

    if payload.event_type_ids:
        event_types = (
            db.query(EventType)
            .filter(EventType.id.in_(payload.event_type_ids))
            .all()
        )
        if len(event_types) != len(set(payload.event_type_ids)):
            return api_response(400, False, "유효하지 않은 event_type_id가 포함되어 있습니다.", None)

    # 요청된 이벤트 타입을 task_event에 저장 (중복 제거)
    task.event_requests.clear()
    for et_id in payload.event_type_ids:
        task.event_requests.append(TaskEvent(event_type_id=et_id))

    task.status = ServiceStatus.PROCESSING
    db.commit()
    db.refresh(task)

    # 실제 GPU 서버로 던질 때의 SSH 예제 (주석 유지)
    # import paramiko
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect(
    #     hostname=GPU_SSH_HOST,
    #     port=GPU_SSH_PORT,
    #     username=GPU_SSH_USER,
    #     key_filename="/root/.ssh/cv-11-3_key.pem",
    # )
    # ssh.exec_command(f"python run_inference.py --task-id {task_id}")
    # ssh.close()

    # 현재는 로컬 예제로 비동기 처리 시뮬레이션
    background_tasks.add_task(simulate_async_processing, task.id, payload.event_type_ids)

    data = {
        "task_id": task.id,
        "video_id": task.video_id,
        "status": task.status.value,
        "requested_event_type_ids": payload.event_type_ids,
    }
    return api_response(202, True, "분석을 시작했습니다.", data)


@router.get("/tasks/{task_id}", summary="분석 확인(폴링)")
async def get_task_status(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        return api_response(404, False, "작업(task)을 찾을 수 없습니다.", None)

    if task.status == ServiceStatus.COMPLETED:
        results = []
        for res in task.results:
            results.append(
                {
                    "result_id": res.id,
                    "event_type": {
                        "event_type_id": res.event_type.id if res.event_type else res.event_type_id,
                        "event_name": res.event_type.event_name if res.event_type else None,
                    },
                    "clip_path": res.clip_path,
                    "occurred_time": res.occurred_time.isoformat() if res.occurred_time else None,
                    "license_plate_img": res.license_plate_img,
                    "license_plate_text": res.license_plate_text,
                    "result_created_at": res.created_at.isoformat() if res.created_at else None,
                }
            )

        data = {
            "task": {
                "task_id": task.id,
                "video_id": task.video_id,
                "status": task.status.value,
            },
            "results": results,
        }
        return api_response(200, True, "분석이 완료되었습니다.", data)

    data = {"task_id": task.id, "status": task.status.value}
    return api_response(200, True, "분석이 진행 중입니다.", data)


def simulate_async_processing(task_id: int, event_type_ids: List[int]) -> None:
    """Lightweight demo to mimic GPU-side processing and DB update."""
    time.sleep(SIMULATED_DELAY_SECONDS)
    session = SessionLocal()
    try:
        task = session.get(Task, task_id)
        if not task:
            return
        if task.status == ServiceStatus.COMPLETED:
            return

        if not event_type_ids:
            # fallback: use all event types or default 1
            event_type_ids = [et.id for et in session.query(EventType).all()] or [1]

        now = datetime.now(timezone.utc)
        for idx, event_type_id in enumerate(event_type_ids, start=1):
            session.add(
                AnalysisResult(
                    task_id=task_id,
                    event_type_id=event_type_id,
                    clip_path=build_example_clip_path(task_id, idx),
                    occurred_time=now,
                    license_plate_img=build_example_plate_path(task_id, idx),
                    license_plate_text=f"11가{task_id:04d}",
                )
            )
        task.status = ServiceStatus.COMPLETED
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
