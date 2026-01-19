import re
import cv2
import numpy as np
from typing import Tuple, Optional
from loguru import logger


def extract_datetime_from_filename(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """
    파일명에서 날짜/시간 추출
    
    Args:
        filename: 파일명 (예: "20260115-11h37m24s_N.avi")
    
    Returns:
        (날짜, 시간) 튜플. 파싱 실패 시 (None, None) 반환
        날짜 형식: "2026-01-15"
        시간 형식: "11:37:24"
    """
    # 정규식 패턴: YYYYMMDD-HhMmSs 형식
    pattern = r"(\d{8})-(\d{1,2})h(\d{1,2})m(\d{1,2})s"
    match = re.search(pattern, filename)
    
    if not match:
        logger.warning(f"파일명에서 날짜/시간을 추출할 수 없습니다: {filename}")
        return (None, None)
    
    date_str = match.group(1)  # YYYYMMDD
    hour = match.group(2)       # H
    minute = match.group(3)     # Mm
    second = match.group(4)     # Ss
    
    # 날짜 형식 변환: YYYYMMDD -> YYYY-MM-DD
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    
    # 시간 형식 변환: HhMmSs -> HH:MM:SS
    formatted_time = f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
    
    logger.info(f"파일명에서 날짜/시간 추출: {formatted_date} {formatted_time}")
    return (formatted_date, formatted_time)


def extract_video_metadata(video_path: str) -> dict:
    """
    영상 메타데이터 추출
    
    Args:
        video_path: 영상 파일 경로
    
    Returns:
        메타데이터 딕셔너리 (fps, duration, total_frames)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"영상을 열 수 없습니다: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    cap.release()
    
    metadata = {
        "fps": fps,
        "duration": duration,
        "total_frames": total_frames
    }
    
    logger.info(f"영상 메타데이터: {metadata}")
    return metadata


def get_frame_at_time(video_path: str, time_seconds: float) -> np.ndarray:
    """
    특정 시간의 프레임 추출
    
    Args:
        video_path: 영상 파일 경로
        time_seconds: 추출할 시간 (초)
    
    Returns:
        프레임 이미지 (numpy array)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"영상을 열 수 없습니다: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(time_seconds * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    
    cap.release()
    
    if not ret:
        raise ValueError(f"프레임을 추출할 수 없습니다: {time_seconds}초")
    
    return frame

