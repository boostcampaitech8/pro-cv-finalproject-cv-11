from uuid import UUID, uuid4
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlmodel import Session, select

from database import engine, Task, Event
from schemas import (
    UploadResponse,
    TaskStatusResponse,
    TaskResultsResponse,
    EventResponse,
    UserInfo
)
from utils.file_utils import save_uploaded_video, create_storage_directories
from services.video_service import process_video_task

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_info: str = Form(...)
):
    """
    영상 업로드 및 분석 작업 시작
    
    Args:
        file: 업로드된 영상 파일
        user_info: 사용자 정보 (JSON 문자열)
        background_tasks: 백그라운드 작업 관리자
    
    Returns:
        작업 ID
    """
    try:
        # 저장소 디렉토리 생성
        create_storage_directories()
        
        # 작업 ID 생성
        task_id = uuid4()
        
        # 영상 파일 저장 (상대 경로)
        video_path = save_uploaded_video(file, task_id)
        
        # Task 생성
        task = Task(
            id=task_id,
            status="pending",
            progress=0,
            current_step="업로드 완료",
            video_path=video_path,
            user_info=user_info
        )
        
        with Session(engine) as session:
            session.add(task)
            session.commit()
        
        logger.info(f"Task created: {task_id}, video saved to: {video_path}")
        
        # 백그라운드 작업 시작
        background_tasks.add_task(process_video_task, task_id)
        
        return UploadResponse(task_id=task_id)
    
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"영상 업로드 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
def get_task_status(task_id: UUID):
    """
    작업 상태 조회
    
    Args:
        task_id: 작업 ID
    
    Returns:
        작업 상태 정보
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="작업을 찾을 수 없습니다"
            )
        
        return TaskStatusResponse(
            status=task.status,
            progress=task.progress,
            current_step=task.current_step,
            error_message=task.error_message
        )


@router.get("/tasks/{task_id}/results", response_model=TaskResultsResponse)
def get_task_results(task_id: UUID):
    """
    분석 결과 조회
    
    Args:
        task_id: 작업 ID
    
    Returns:
        분석 결과 (이벤트 리스트)
    """
    with Session(engine) as session:
        # Task 조회
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="작업을 찾을 수 없습니다"
            )
        
        # Event 조회
        statement = select(Event).where(Event.task_id == task_id)
        events = session.exec(statement).all()
        
        # EventResponse로 변환
        event_responses = []
        for event in events:
            event_responses.append(EventResponse(
                event_id=event.id,
                event_type=event.event_type,
                violation_type=event.violation_type,
                timestamp=event.timestamp,
                risk_level=event.risk_level,
                vehicle_number=event.vehicle_number,
                location=event.location,
                date=event.date,
                time=event.time,
                title=event.title,
                content=event.content,
                video_clip_path=event.video_clip_path,
                images={
                    "key_frame": event.key_frame_path,
                    "vehicle_crop": event.vehicle_crop_path,
                    "license_plate_crop": event.license_crop_path
                }
            ))
        
        return TaskResultsResponse(
            task_id=task_id,
            status=task.status,
            events=event_responses
        )

