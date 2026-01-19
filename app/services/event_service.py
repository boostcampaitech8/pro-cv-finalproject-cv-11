import random
from uuid import uuid4
from typing import List, Optional
from loguru import logger

# 고정된 이벤트 구간
EVENT_INTERVALS = [
    (1.0, 5.0),   # 이벤트 1: 1~5초
    (6.0, 10.0),  # 이벤트 2: 6~10초
    (11.0, 15.0)  # 이벤트 3: 11~15초
]

# 핵심 프레임 추출 시간 (각 구간의 중간)
KEY_FRAME_TIMES = [3.0, 8.0, 13.0]

# 위반 이벤트 유형 (0번 항목)
EVENT_TYPES = [
    "안전거리 미확보",
    "제차 신호 조작 불이행(방향지시등)",
    "적색·황색 신호등에 정지선을 넘는 행위",
    "차선 위반"
]

# 위험도
RISK_LEVELS = ["높음", "중간", "낮음"]

# 위반 신고 유형 (1번 항목) - 고정
VIOLATION_TYPE = "교통위반(교통단속 포함)"


def detect_dummy_events(
    video_path: str,
    video_date: Optional[str],
    video_time: Optional[str]
) -> List[dict]:
    """
    더미 이벤트 검출 (고정된 3개 구간)
    
    Args:
        video_path: 영상 파일 경로
        video_date: 비디오 날짜 (파일명에서 추출, None일 수 있음)
        video_time: 비디오 시간 (파일명에서 추출, None일 수 있음)
    
    Returns:
        이벤트 리스트
    """
    events = []
    
    for idx, (start_time, end_time) in enumerate(EVENT_INTERVALS):
        # 이벤트 타입 랜덤 선택
        event_type = random.choice(EVENT_TYPES)
        
        # 위험도 랜덤 할당
        risk_level = random.choice(RISK_LEVELS)
        
        # 발생 시각 계산
        if video_date and video_time:
            # 비디오 시간을 datetime으로 변환하여 구간 시작 시간 추가
            from datetime import datetime, timedelta
            try:
                video_datetime = datetime.strptime(f"{video_date} {video_time}", "%Y-%m-%d %H:%M:%S")
                event_datetime = video_datetime + timedelta(seconds=start_time)
                event_date = event_datetime.strftime("%Y-%m-%d")
                event_time = event_datetime.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                logger.warning(f"날짜/시간 계산 실패: {e}")
                event_date = None
                event_time = None
        else:
            event_date = None
            event_time = None
        
        # 타임스탬프 (영상 내 시간)
        timestamp = f"{int(start_time // 60):02d}:{int(start_time % 60):02d}:{int((start_time % 1) * 60):02d}"
        
        event = {
            "event_id": uuid4(),
            "event_type": event_type,  # 0번 항목
            "violation_type": VIOLATION_TYPE,  # 1번 항목
            "timestamp": timestamp,
            "risk_level": risk_level,
            "start_time": start_time,
            "end_time": end_time,
            "key_frame_time": KEY_FRAME_TIMES[idx],
            "date": event_date,
            "time": event_time,
            "event_index": idx  # 번호판 매핑용
        }
        
        events.append(event)
        logger.info(f"이벤트 {idx + 1} 검출: {event_type} ({start_time}~{end_time}초)")
    
    return events

