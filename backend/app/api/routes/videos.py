from pathlib import Path

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.utils import api_response
from app.core.config import GCS_BUCKET_NAME
from app.models.analysis import ServiceStatus, Task
from app.models.video import Video
from app.services.storage import save_upload_file

router = APIRouter()


@router.post("/videos", summary="비디오 업로드 (+task UPLOADING)", status_code=201)
async def upload_video(
    file: UploadFile = File(..., description="업로드할 영상 파일"),
    db: Session = Depends(get_db),
):
    """
    1) 비디오 파일을 로컬 스토리지(`storage/videos`)에 저장
    2) Video + Task(UPLOADING) 레코드를 생성

    실제 GCS 업로드 시에는 `save_upload_file` 대신 주석의 예제를 사용할 수 있다.
    """
    if not file:
        return api_response(400, False, "업로드할 파일이 없습니다.", None)

    # --- Local example flow (active) ---
    stored_path = save_upload_file(file)
    filepath = str(stored_path)

    # --- GCP flow (prepare & comment) ---
    # if GCS_BUCKET_NAME:
    #     # 예시: gs://bucket/videos/<filename>
    #     gcs_object_path = f"videos/{file.filename}"
    #     filepath = upload_to_gcs(file, GCS_BUCKET_NAME, gcs_object_path)
    # else:
    #     filepath = str(save_upload_file(file))

    video = Video(filename=file.filename, filepath=filepath)
    db.add(video)
    db.flush()  # to populate video.id

    task = Task(video_id=video.id, status=ServiceStatus.UPLOADING)
    db.add(task)
    db.commit()
    db.refresh(video)
    db.refresh(task)

    data = {
        "video": {
            "video_id": video.id,
            "filename": video.filename,
            "filepath": video.filepath,
            "uploaded_at": video.uploaded_at.isoformat(),
        },
        "task": {
            "task_id": task.id,
            "video_id": task.video_id,
            "status": task.status.value,
            "task_created_at": task.created_at.isoformat(),
        },
    }
    return api_response(201, True, "비디오 업로드가 완료되었습니다.", data)


@router.get("/videos/file", summary="비디오 반환(다운로드/스트리밍)")
async def get_video_file(
    filename: str = Query(..., description="비디오 파일명"),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.filename == filename).one_or_none()
    if not video:
        return api_response(404, False, "해당 filename의 비디오를 찾을 수 없습니다.", None)

    file_path = Path(video.filepath)
    if not file_path.exists():
        return api_response(404, False, "로컬 저장소에서 파일을 찾을 수 없습니다.", None)

    # --- GCP에서 직접 스트리밍 시 (준비용 주석) ---
    # from google.cloud import storage
    # client = storage.Client()
    # bucket = client.bucket(GCS_BUCKET_NAME)
    # blob = bucket.blob(video.filepath)
    # return StreamingResponse(blob.download_as_bytes(), media_type="video/mp4")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=video.filename,
    )


@router.get("/videos/{video_id}", summary="비디오 메타 + 현재 상태 조회")
async def get_video_meta(video_id: int, db: Session = Depends(get_db)):
    video = db.get(Video, video_id)
    if not video:
        return api_response(404, False, "비디오를 찾을 수 없습니다.", None)

    task = (
        db.query(Task)
        .filter(Task.video_id == video.id)
        .order_by(Task.created_at.desc())
        .first()
    )

    data = {
        "video_id": video.id,
        "filename": video.filename,
        "filepath": video.filepath,
        "uploaded_at": video.uploaded_at.isoformat() if video.uploaded_at else None,
        "task": None,
    }
    if task:
        data["task"] = {
            "task_id": task.id,
            "status": task.status.value,
        }

    return api_response(200, True, "비디오 정보를 조회했습니다.", data)


@router.get("/videos/{video_id}/results", summary="특정 비디오의 분석 결과 목록 조회")
async def get_video_results(video_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.video_id == video_id).one_or_none()
    if not task:
        return api_response(404, False, "해당 비디오의 작업(task)을 찾을 수 없습니다.", None)

    results = task.results
    serialized = []
    for res in results:
        serialized.append(
            {
                "result_id": res.id,
                "event_type_id": res.event_type_id,
                "clip_path": res.clip_path,
                "occurred_time": res.occurred_time.isoformat() if res.occurred_time else None,
                "license_plate_text": res.license_plate_text,
                "license_plate_img": res.license_plate_img,
            }
        )

    data = {
        "video_id": video_id,
        "results": serialized,
    }
    return api_response(200, True, "분석 결과 목록을 조회했습니다.", data)
