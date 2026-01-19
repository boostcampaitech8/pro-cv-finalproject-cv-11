import cv2
from uuid import UUID
from loguru import logger
from utils.file_utils import generate_file_path


def create_video_clip(
    video_path: str,
    start_time: float,
    end_time: float,
    task_id: UUID,
    event_id: UUID
) -> str:
    """
    이벤트 구간 영상 클립 생성
    
    Args:
        video_path: 원본 영상 파일 경로
        start_time: 시작 시간 (초)
        end_time: 종료 시간 (초)
        task_id: 작업 ID
        event_id: 이벤트 ID
    
    Returns:
        저장된 클립의 상대 경로
    """
    # 파일 경로 생성
    clip_path = generate_file_path(task_id, event_id, "clip")
    
    # TODO: GCP migration - 이 부분을 클라우드 스토리지로 변경
    # 영상 열기
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"영상을 열 수 없습니다: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # VideoWriter 설정 (H.264 코덱 사용 - 브라우저 호환성)
    # 참고: 'avc1' 또는 'H264' 사용, 시스템에 따라 다를 수 있음
    '''
        video가 재생되지 않는 에러 발생함.
        코덱 문젠가 싶어 avc1로 변경해 봄 -> 아예 ui조차 안 나오는 에러 발생.
        일단 코덱 문제는 아니라고 판단됨.
    '''
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 코덱
    out = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))
        
    # 시작 프레임으로 이동
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    # 프레임 읽기 및 저장
    current_frame = start_frame
    while current_frame <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1
    
    cap.release()
    out.release()
    
    logger.info(f"영상 클립 저장: {clip_path} ({start_time}~{end_time}초)")
    return clip_path


def process_video_task(task_id: UUID):
    """
    영상 분석 작업 처리 (Background Task)
    
    Args:
        task_id: 작업 ID
    """
    from sqlmodel import Session
    from database import engine, Task, Event
    from config import config
    from utils.video_utils import extract_video_metadata, extract_datetime_from_filename
    from utils.file_utils import generate_file_path
    from services.event_service import detect_dummy_events
    from services.image_service import (
        extract_key_frame,
        extract_vehicle_crop,
        get_dummy_plate_image,
        extract_license_plate_dummy,
        copy_license_plate_image
    )
    # create_video_clip은 같은 파일에 있으므로 직접 호출
    from services.llm_service import generate_title_and_content
    import json
    from pathlib import Path
    
    try:
        with Session(engine) as session:
            # Task 조회
            task = session.get(Task, task_id)
            if not task:
                logger.error(f"Task를 찾을 수 없습니다: {task_id}")
                return
            
            # 상태를 processing으로 변경
            task.status = "processing"
            task.progress = 0
            task.current_step = "영상 메타데이터 추출 중"
            session.commit()
            session.refresh(task)
            
            logger.info(f"작업 시작: {task_id}")
            
            # 10%: 영상 메타데이터 추출
            video_path = task.video_path
            # 상대 경로를 절대 경로로 변환
            if not Path(video_path).is_absolute():
                video_path = str(config.project_root / video_path.lstrip("./"))
            
            metadata = extract_video_metadata(video_path)
            task.progress = 10
            task.current_step = "영상 메타데이터 추출 완료"
            session.commit()
            
            # 파일명에서 날짜/시간 추출
            filename = Path(video_path).name
            video_date, video_time = extract_datetime_from_filename(filename)
            
            # 30%: 이벤트 검출
            task.progress = 30
            task.current_step = "이벤트 검출 중"
            session.commit()
            
            events = detect_dummy_events(video_path, video_date, video_time)
            
            # 사용자 정보 파싱
            user_info = json.loads(task.user_info)
            llm_provider = user_info.get("llm_provider", "사용 안 함")
            llm_api_key = user_info.get("llm_api_key")
            
            # 50%: 이미지 추출
            task.progress = 50
            task.current_step = "이미지 추출 중"
            session.commit()
            
            for event_data in events:
                event_id = event_data["event_id"]
                
                # 핵심 프레임 추출
                key_frame_path = extract_key_frame(
                    video_path,
                    event_data["key_frame_time"],
                    task_id,
                    event_id
                )
                
                # 차량 Crop
                vehicle_crop_path = extract_vehicle_crop(
                    key_frame_path,
                    task_id,
                    event_id
                )
                
                # 번호판 이미지 복사
                plate_image_path = get_dummy_plate_image(event_data["event_index"])
                license_crop_path = copy_license_plate_image(
                    plate_image_path,
                    task_id,
                    event_id
                )
            
            # 70%: 영상 클립 생성
            task.progress = 70
            task.current_step = "영상 클립 생성 중"
            session.commit()
            
            for event_data in events:
                event_id = event_data["event_id"]
                clip_path = create_video_clip(
                    video_path,
                    event_data["start_time"],
                    event_data["end_time"],
                    task_id,
                    event_id
                )
                event_data["video_clip_path"] = clip_path
            
            # 90%: 번호판 OCR
            task.progress = 90
            task.current_step = "번호판 OCR 중"
            session.commit()
            
            for event_data in events:
                vehicle_number = extract_license_plate_dummy(event_data["event_index"])
                event_data["vehicle_number"] = vehicle_number
            
            # LLM으로 제목/내용 생성
            for event_data in events:
                llm_result = generate_title_and_content(
                    event_data["event_type"],
                    event_data["violation_type"],
                    llm_provider,
                    llm_api_key
                )
                event_data["title"] = llm_result["title"]
                event_data["content"] = llm_result["content"]
            
            # Event 저장
            for event_data in events:
                # 이미지 경로 가져오기
                key_frame_path = generate_file_path(task_id, event_data["event_id"], "key_frame")
                vehicle_crop_path = generate_file_path(task_id, event_data["event_id"], "vehicle_crop")
                license_crop_path = generate_file_path(task_id, event_data["event_id"], "license_crop")
                
                event = Event(
                    id=event_data["event_id"],
                    task_id=task_id,
                    event_type=event_data["event_type"],
                    violation_type=event_data["violation_type"],
                    timestamp=event_data["timestamp"],
                    risk_level=event_data["risk_level"],
                    vehicle_number=event_data["vehicle_number"],
                    location=None,  # GPS는 나중에
                    date=event_data["date"],
                    time=event_data["time"],
                    title=event_data["title"],
                    content=event_data["content"],
                    video_clip_path=event_data.get("video_clip_path"),
                    key_frame_path=key_frame_path,
                    vehicle_crop_path=vehicle_crop_path,
                    license_crop_path=license_crop_path
                )
                session.add(event)
            
            # 100%: 완료
            task.progress = 100
            task.status = "completed"
            task.current_step = "완료"
            session.commit()
            
            logger.info(f"작업 완료: {task_id}")
    
    except Exception as e:
        logger.error(f"작업 실패: {task_id}, 오류: {str(e)}")
        with Session(engine) as session:
            task = session.get(Task, task_id)
            if task:
                task.status = "failed"
                task.error_message = str(e)
                task.current_step = "오류 발생"
                session.commit()
