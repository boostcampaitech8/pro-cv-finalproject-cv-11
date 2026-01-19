import shutil
from uuid import UUID
from pathlib import Path
import cv2
import numpy as np
from loguru import logger
from config import config

# 번호판 매핑
PLATE_NUMBERS = {
    0: "154러7070",
    1: "157고4895",
    2: "120서6041"
}


def extract_key_frame(
    video_path: str,
    time_seconds: float,
    task_id: UUID,
    event_id: UUID
) -> str:
    """
    핵심 프레임 추출
    
    Args:
        video_path: 영상 파일 경로
        time_seconds: 추출할 시간 (초)
        task_id: 작업 ID
        event_id: 이벤트 ID
    
    Returns:
        저장된 이미지의 상대 경로
    """
    from utils.video_utils import get_frame_at_time
    from utils.file_utils import generate_file_path
    
    # 프레임 추출
    frame = get_frame_at_time(video_path, time_seconds)
    
    # 파일 경로 생성
    file_path = generate_file_path(task_id, event_id, "key_frame")
    
    # TODO: GCP migration - 이 부분을 클라우드 스토리지로 변경
    # 이미지 저장
    cv2.imwrite(file_path, frame)
    
    logger.info(f"핵심 프레임 저장: {file_path}")
    return file_path


def extract_vehicle_crop(
    key_frame_path: str,
    task_id: UUID,
    event_id: UUID
) -> str:
    """
    차량 Crop 이미지 생성 (더미)
    
    Args:
        key_frame_path: 핵심 프레임 경로
        task_id: 작업 ID
        event_id: 이벤트 ID
    
    Returns:
        저장된 이미지의 상대 경로
    """
    from utils.file_utils import generate_file_path
    
    # TODO: GCP migration - 이 부분을 클라우드 스토리지로 변경
    # 이미지 읽기
    img = cv2.imread(key_frame_path)
    if img is None:
        raise ValueError(f"이미지를 읽을 수 없습니다: {key_frame_path}")
    
    # 더미 bounding box: 전체 프레임의 중앙 50% 영역
    h, w = img.shape[:2]
    x1 = int(w * 0.25)
    y1 = int(h * 0.25)
    x2 = int(w * 0.75)
    y2 = int(h * 0.75)
    
    crop = img[y1:y2, x1:x2]
    
    # 파일 경로 생성
    file_path = generate_file_path(task_id, event_id, "vehicle_crop")
    
    # 이미지 저장
    cv2.imwrite(file_path, crop)
    
    logger.info(f"차량 Crop 저장: {file_path}")
    return file_path


def get_dummy_plate_image(event_index: int) -> str:
    """
    더미 번호판 이미지 경로 반환 (상대 경로)
    
    Args:
        event_index: 이벤트 인덱스 (0, 1, 2)
    
    Returns:
        더미 번호판 이미지의 상대 경로
    """
    plate_files = {
        0: f"{config.dummy_plate_images_path}/plate1.jpg",
        1: f"{config.dummy_plate_images_path}/plate2.jpg",
        2: f"{config.dummy_plate_images_path}/plate3.jpg"
    }
    
    if event_index not in plate_files:
        raise ValueError(f"알 수 없는 이벤트 인덱스: {event_index}")
    
    return plate_files[event_index]


def extract_license_plate_dummy(event_index: int) -> str:
    """
    더미 번호판 OCR (하드코딩)
    
    Args:
        event_index: 이벤트 인덱스 (0, 1, 2)
    
    Returns:
        차량 번호
    """
    if event_index not in PLATE_NUMBERS:
        raise ValueError(f"알 수 없는 이벤트 인덱스: {event_index}")
    
    plate_number = PLATE_NUMBERS[event_index]
    logger.info(f"번호판 OCR (더미): {plate_number}")
    return plate_number


def copy_license_plate_image(
    plate_image_path: str,
    task_id: UUID,
    event_id: UUID
) -> str:
    """
    더미 번호판 이미지를 저장소로 복사
    
    Args:
        plate_image_path: 원본 번호판 이미지 경로
        task_id: 작업 ID
        event_id: 이벤트 ID
    
    Returns:
        저장된 이미지의 상대 경로
    """
    from utils.file_utils import generate_file_path
    
    # 파일 경로 생성
    dest_path = generate_file_path(task_id, event_id, "license_crop")
    
    # TODO: GCP migration - 이 부분을 클라우드 스토리지로 변경
    # 파일 복사
    shutil.copy2(plate_image_path, dest_path)
    
    logger.info(f"번호판 이미지 복사: {dest_path}")
    return dest_path

