"""
서버 비즈니스 로직 (더미 데이터 사용)
"""
import json
import os
from typing import List, Dict, Optional
from pathlib import Path


def generate_dummy_events() -> List[Dict]:
    """더미 이벤트 데이터를 JSON 파일에서 로드"""
    # backend 폴더 기준으로 경로 설정
    current_dir = Path(__file__).parent
    json_path = current_dir / "dummy_events.json"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
        return events
    except FileNotFoundError:
        # 파일이 없으면 기본 더미 데이터 반환
        return _get_default_dummy_events()
    except json.JSONDecodeError:
        return _get_default_dummy_events()


def _get_default_dummy_events() -> List[Dict]:
    """기본 더미 이벤트 데이터"""
    return [
        {
            "event_id": 1,
            "event_type": "급차로 변경",
            "violation_type": "교통위반(교통단속 포함)",
            "timestamp": "00:01:23",
            "risk_level": "높음",
            "vehicle_number": "12가3456",
            "location": "서울시 강남구 테헤란로 123",
            "date": "2024-01-15",
            "time": "2024-01-15 14:23:45",
            "title": "급차로 변경 위반 차량 신고",
            "content": "해당 차량이 급격하게 차로를 변경하여 위험한 상황을 초래했습니다.",
            "video_clip_path": None,
            "images": {
                "key_frame": None,
                "vehicle_crop": None,
                "license_plate_crop": None
            }
        }
    ]


def detect_events(video_path: str, user_info: Dict) -> List[Dict]:
    """
    영상에서 위반 이벤트 검출 (더미 데이터 반환)
    
    Args:
        video_path: 영상 파일 경로
        user_info: 사용자 정보
        
    Returns:
        검출된 이벤트 리스트
    """
    # TODO: 실제 모델 연결
    # 프로토타입: 더미 데이터 반환
    return generate_dummy_events()


def extract_video_metadata(video_path: str) -> Dict:
    """
    영상 메타데이터 추출 (더미 데이터 반환)
    
    Args:
        video_path: 영상 파일 경로
        
    Returns:
        메타데이터 딕셔너리
    """
    # TODO: 실제 구현
    return {
        "recording_date": "2024-01-15",
        "recording_time": "14:20:00",
        "fps": 30
    }


def extract_location_info(video_path: str) -> Optional[str]:
    """
    GPS 위치 정보 추출
    
    Args:
        video_path: 영상 파일 경로
        
    Returns:
        위치 정보 문자열 (없으면 None)
    """
    # TODO: 실제 구현
    return None


def generate_llm_content(
    event_type: str, 
    violation_type: str, 
    event_details: Optional[Dict] = None,
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    LLM을 사용하여 제목과 신고 내용 생성 (템플릿 사용)
    
    Args:
        event_type: 이벤트 타입
        violation_type: 위반 유형
        event_details: 이벤트 상세 정보
        api_key: LLM API 키 (선택)
        
    Returns:
        {"title": "...", "content": "..."}
    """
    # TODO: LLM API 연동
    # 프로토타입: 기본 템플릿 사용
    
    title = f"{event_type} 위반 차량 신고"
    
    if event_details:
        location = event_details.get("location", "")
        vehicle_number = event_details.get("vehicle_number", "")
        timestamp = event_details.get("timestamp", "")
        date = event_details.get("date", "")
        
        content = (
            f"{date} {timestamp}경, {location} 부근에서 "
            f"차량번호 {vehicle_number}이(가) {event_type} 위반을 저질렀습니다. "
            f"상세 내용은 첨부된 영상과 사진을 참고해주세요."
        )
    else:
        content = (
            f"해당 차량이 {event_type} 위반을 저질렀습니다. "
            f"상세 내용은 첨부된 영상과 사진을 참고해주세요."
        )
    
    return {
        "title": title,
        "content": content
    }


def format_report_data(event: Dict, user_info: Dict) -> Dict:
    """
    안전신문고 신고 양식 데이터 포맷팅
    
    Args:
        event: 이벤트 정보
        user_info: 사용자 정보
        
    Returns:
        신고 양식 데이터
    """
    # 시간에서 일자 제거 (시간만 표시)
    time_str = event.get("time", "")
    if " " in time_str:
        time_str = time_str.split(" ")[1]
    
    return {
        "1. 자동차·교통 위반 신고 유형": event.get("violation_type", ""),
        "2. 사진/동영상(첨부)": "동영상 1개, 핵심 사진 1장, 차량 crop 1장, 번호판 crop 1장",
        "3. 신고 발생 지역": event.get("location", "위치 정보 없음"),
        "4. 제목": event.get("title", ""),
        "5. 신고 내용": event.get("content", ""),
        "6. 차량 번호": event.get("vehicle_number", ""),
        "7. 발생 일자": event.get("date", ""),
        "8. 발생 시각": time_str,
        "9. 휴대전화": user_info.get("phone", ""),
        "10. 인증번호": user_info.get("auth_code", ""),
        "11. 신고 내용 공유": user_info.get("share_content", "아니요"),
        "12. 인적 사항": user_info.get("personal_info", "")
    }

