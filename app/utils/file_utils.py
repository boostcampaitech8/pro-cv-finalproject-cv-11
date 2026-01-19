import os
from pathlib import Path
from uuid import UUID
from fastapi import UploadFile
from loguru import logger
from config import config


def create_storage_directories():
    """필요한 저장소 디렉토리 생성 (상대 경로)"""
    directories = [
        f"{config.storage_base_path}/videos",
        f"{config.storage_base_path}/clips",
        f"{config.storage_base_path}/images/key_frames",
        f"{config.storage_base_path}/images/vehicle_crops",
        f"{config.storage_base_path}/images/license_crops"
    ]
    
    for directory in directories:
        # TODO: GCP migration - 이 부분을 클라우드 스토리지로 변경
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"디렉토리 생성 확인: {directory}")


def save_uploaded_video(file: UploadFile, task_id: UUID) -> str:
    """
    업로드된 영상 저장
    
    Args:
        file: 업로드된 파일
        task_id: 작업 ID
    
    Returns:
        저장된 파일의 상대 경로
    """
    # 파일명 생성: task_id_원본파일명
    filename = f"{task_id}_{file.filename}"
    file_path = f"{config.storage_base_path}/videos/{filename}"
    
    # TODO: GCP migration - 이 부분을 클라우드 스토리지로 변경
    # 실제 파일 저장
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    
    logger.info(f"영상 저장 완료: {file_path}")
    return file_path


def generate_file_path(task_id: UUID, event_id: UUID, file_type: str) -> str:
    """
    파일 경로 생성 (상대 경로)
    
    Args:
        task_id: 작업 ID
        event_id: 이벤트 ID
        file_type: 파일 타입 (key_frame, vehicle_crop, license_crop, clip)
    
    Returns:
        상대 경로 문자열
    """
    base_paths = {
        "key_frame": f"{config.storage_base_path}/images/key_frames",
        "vehicle_crop": f"{config.storage_base_path}/images/vehicle_crops",
        "license_crop": f"{config.storage_base_path}/images/license_crops",
        "clip": f"{config.storage_base_path}/clips"
    }
    
    if file_type not in base_paths:
        raise ValueError(f"알 수 없는 파일 타입: {file_type}")
    
    base_path = base_paths[file_type]
    extension = ".jpg" if file_type != "clip" else ".mp4"
    filename = f"{task_id}_{event_id}{extension}"
    
    return f"{base_path}/{filename}"

