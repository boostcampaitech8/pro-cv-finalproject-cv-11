import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
import requests
import time

# 페이지 설정
st.set_page_config(
    page_title="교통 위반 신고 자동화 시스템",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 설정
# ============================================================================

# FastAPI 서버 URL (환경 변수로 설정 가능)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
SERVER_TIMEOUT = 30  # 서버 연결 타임아웃 (초)

# ============================================================================
# FastAPI 서버 통신 함수들
# ============================================================================

def check_server_connection() -> bool:
    """FastAPI 서버 연결 가능 여부 확인"""
    return False
    try:
        response = requests.get(
            f"{API_BASE_URL.replace('/api/v1', '')}/health",
            timeout=5
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def upload_video_to_server(video_file, user_info: Dict) -> Optional[str]:
    """
    영상을 FastAPI 서버에 업로드하고 작업 ID 반환
    
    Args:
        video_file: 업로드된 영상 파일
        user_info: 사용자 정보 딕셔너리
        
    Returns:
        작업 ID (성공 시) 또는 None (실패 시)
    """
    try:
        # 파일 포인터를 처음으로 이동
        video_file.seek(0)
        
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files={"file": (video_file.name, video_file, video_file.type)},
            data={"user_info": json.dumps(user_info)},
            timeout=SERVER_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        return result.get("task_id")
    except requests.exceptions.RequestException as e:
        return None


def get_task_status(task_id: str) -> Optional[Dict]:
    """
    작업 상태 조회
    
    Args:
        task_id: 작업 ID
        
    Returns:
        상태 정보 딕셔너리 또는 None
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/tasks/{task_id}/status",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def get_task_results(task_id: str) -> Optional[Dict]:
    """
    분석 결과 조회
    
    Args:
        task_id: 작업 ID
        
    Returns:
        결과 딕셔너리 또는 None
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/tasks/{task_id}/results",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def process_with_server(task_id: str) -> List[Dict]:
    """
    서버에서 비동기로 처리되는 작업 추적 및 결과 반환
    
    Args:
        task_id: 작업 ID
        
    Returns:
        검출된 이벤트 리스트
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    max_attempts = 300  # 최대 5분 대기 (1초 간격)
    attempt = 0
    
    while attempt < max_attempts:
        status = get_task_status(task_id)
        
        if not status:
            progress_bar.empty()
            status_text.empty()
            st.error("서버와의 연결이 끊어졌습니다.")
            return []
        
        task_status = status.get("status", "unknown")
        progress = status.get("progress", 0)
        current_step = status.get("current_step", "처리 중...")
        
        # 진행률 업데이트
        progress_bar.progress(progress / 100)
        status_text.text(f"진행률: {progress}% - {current_step}")
        
        if task_status == "completed":
            # 결과 조회
            results = get_task_results(task_id)
            progress_bar.empty()
            status_text.empty()
            
            if results and "events" in results:
                return results["events"]
            else:
                st.error("결과를 가져올 수 없습니다.")
                return []
        
        elif task_status == "failed":
            progress_bar.empty()
            status_text.empty()
            error_msg = status.get("error", "알 수 없는 오류")
            st.error(f"분석 실패: {error_msg}")
            return []
        
        # 1초 대기 후 재시도
        time.sleep(1)
        attempt += 1
    
    # 타임아웃
    progress_bar.empty()
    status_text.empty()
    st.error("분석 시간이 초과되었습니다.")
    return []




# ============================================================================
# 유틸리티 함수들 (확장 가능하도록 분리)
# ============================================================================

def generate_dummy_events() -> List[Dict]:
    """더미 이벤트 데이터를 JSON 파일에서 로드 (실제 모델 연결 시 교체 예정)"""
    # 현재 파일의 디렉토리 경로 가져오기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "dummy_events", "events.json")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
        return events
    except FileNotFoundError:
        st.error(f"더미 이벤트 파일을 찾을 수 없습니다: {json_path}")
        return []
    except json.JSONDecodeError:
        st.error(f"더미 이벤트 JSON 파일 파싱 오류: {json_path}")
        return []


def detect_events(video_file, user_info: Dict) -> List[Dict]:
    """
    영상에서 위반 이벤트 검출
    - 서버가 있으면 FastAPI 호출
    - 서버가 없으면 더미 데이터 반환
    
    Args:
        video_file: 업로드된 영상 파일
        user_info: 사용자 정보 딕셔너리
        
    Returns:
        검출된 이벤트 리스트
    """
    # 서버 연결 확인
    if check_server_connection():
        # 서버에 업로드 시도
        task_id = upload_video_to_server(video_file, user_info)
        
        if task_id:
            # 서버가 있으면 비동기 처리
            st.info("🔄 서버에 연결되었습니다. 분석을 시작합니다...")
            return process_with_server(task_id)
        else:
            # 업로드 실패 시 더미 데이터 사용
            st.warning("⚠️ 서버 업로드에 실패했습니다. 더미 데이터를 사용합니다.")
            return generate_dummy_events()
    else:
        # 서버가 없으면 더미 데이터 반환 (개발/테스트용)
        st.info("ℹ️ 서버에 연결할 수 없습니다. 더미 데이터를 사용합니다.")
        return generate_dummy_events()


def extract_video_metadata(video_file) -> Dict:
    """
    영상 메타데이터 추출 (발생 시각 등)
    
    Args:
        video_file: 업로드된 영상 파일
        
    Returns:
        메타데이터 딕셔너리
    """
    # TODO: 실제 구현
    # - 동영상에 저장된 시간 정보 추출
    # - 단위시간 당 프레임 수 계산
    # - 탐지 구간의 첫 번째 프레임 촬영 시각 계산
    
    return {
        "recording_date": "2024-01-15",
        "recording_time": "14:20:00",
        "fps": 30
    }


def extract_location_info(video_file) -> Optional[str]:
    """
    GPS 위치 정보 추출
    
    Args:
        video_file: 업로드된 영상 파일
        
    Returns:
        위치 정보 문자열 (없으면 None)
    """
    # TODO: 실제 구현
    # - PIL.ExifTags로 위치 정보 추출
    # - GPS Tracker 연동 고려
    # - 프레임별 시간과 GPS 기록 매칭
    
    return None


def generate_llm_content(event_type: str, violation_type: str, api_key: Optional[str] = None) -> Dict[str, str]:
    """
    LLM을 사용하여 제목과 신고 내용 생성
    
    Args:
        event_type: 이벤트 타입
        violation_type: 위반 유형
        api_key: LLM API 키 (선택)
        
    Returns:
        {"title": "...", "content": "..."}
    """
    # TODO: LLM API 연동
    # - 사용자가 LLM 사용 여부 선택
    # - API 키 입력 받기
    # - 프롬프트 기반 제목/내용 생성
    
    # 프로토타입: 기본 템플릿 사용
    return {
        "title": f"{event_type} 위반 차량 신고",
        "content": f"해당 차량이 {event_type} 위반을 저질렀습니다. 상세 내용은 첨부된 영상과 사진을 참고해주세요."
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
    return {
        "1. 자동차·교통 위반 신고 유형": event.get("violation_type", ""),
        "2. 사진/동영상(첨부)": "동영상 1개, 핵심 사진 1장, 차량 crop 1장, 번호판 crop 1장",
        "3. 신고 발생 지역": event.get("location", "위치 정보 없음"),
        "4. 제목": event.get("title", ""),
        "5. 신고 내용": event.get("content", ""),
        "6. 차량 번호": event.get("vehicle_number", ""),
        "7. 발생 일자": event.get("date", ""),
        "8. 발생 시각": event.get("time", ""),
        "9. 휴대전화": user_info.get("phone", ""),
        "10. 인증번호": user_info.get("auth_code", ""),
        "11. 신고 내용 공유": user_info.get("share_content", "아니요"),
        "12. 인적 사항": user_info.get("personal_info", "")
    }


# ============================================================================
# UI 컴포넌트 함수들 (확장 가능하도록 분리)
# ============================================================================

def render_user_input_section():
    """사용자 입력 섹션 렌더링"""
    st.header("📹 영상 업로드 및 사용자 정보")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        video_file = st.file_uploader(
            "주행 영상 업로드",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="블랙박스 또는 주행 영상을 업로드해주세요."
        )
        
        if video_file:
            st.success(f"✅ 영상 업로드 완료: {video_file.name}")
            file_size = len(video_file.read()) / (1024 * 1024)  # MB
            video_file.seek(0)  # 파일 포인터 리셋
            st.caption(f"파일 크기: {file_size:.2f} MB")
    
    with col2:
        st.subheader("사용자 정보")
        phone = st.text_input("휴대전화", placeholder="010-1234-5678")
        share_content = st.radio(
            "신고 내용 공유",
            ["아니요", "예"],
            index=0,
            help="신고 내용을 공유하시겠습니까?"
        )
        
        # 인적 사항 (나중에 추가 예정)
        personal_info = ""
        with st.expander("인적 사항 (선택사항)"):
            personal_info = st.text_area("인적 사항", placeholder="추후 추가 예정", value="")
    
    return video_file, {
        "phone": phone,
        "share_content": share_content,
        "personal_info": personal_info
    }


def render_llm_option():
    """LLM 사용 옵션 렌더링"""
    use_llm = st.checkbox(
        "제목 및 신고 내용을 LLM으로 자동 생성하시겠습니까?",
        value=False,
        help="체크 시 LLM API 키를 입력하여 제목과 신고 내용을 자동으로 생성합니다."
    )
    
    api_key = None
    if use_llm:
        api_key = st.text_input(
            "LLM API 키",
            type="password",
            placeholder="API 키를 입력하세요"
        )
    
    return use_llm, api_key


def render_event_summary(events: List[Dict]):
    """검출 결과 요약 렌더링"""
    st.header("📊 검출 결과 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_events = len(events)
    high_risk = len([e for e in events if e.get("risk_level") == "높음"])
    medium_risk = len([e for e in events if e.get("risk_level") == "중간"])
    low_risk = len([e for e in events if e.get("risk_level") == "낮음"])
    
    with col1:
        st.metric("총 검출 이벤트", total_events)
    with col2:
        st.metric("높은 위험도", high_risk, delta=None)
    with col3:
        st.metric("중간 위험도", medium_risk, delta=None)
    with col4:
        st.metric("낮은 위험도", low_risk, delta=None)
    
    # 필터링 옵션
    st.subheader("필터 옵션")
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        risk_filter = st.multiselect(
            "위험도 필터",
            ["높음", "중간", "낮음"],
            default=["높음", "중간", "낮음"]
        )
    
    with filter_col2:
        sort_option = st.selectbox(
            "정렬 기준",
            ["시간순", "위험도순", "이벤트 타입순"]
        )
    
    return risk_filter, sort_option


def render_event_details(event: Dict, user_info: Dict, use_llm: bool, api_key: Optional[str]):
    """개별 이벤트 상세 정보 렌더링 (아코디언 방식)"""
    
    # LLM으로 제목/내용 생성 (필요시)
    if use_llm and api_key:
        llm_content = generate_llm_content(event["event_type"], event["violation_type"], api_key)
        event["title"] = llm_content["title"]
        event["content"] = llm_content["content"]
    
    # 아코디언으로 상세 정보 표시
    with st.expander(
        f"🚨 이벤트 #{event['event_id']}: {event['event_type']} | "
        f"시간: {event['timestamp']} | 위험도: {event['risk_level']}",
        expanded=False
    ):
        # 탭으로 정보 분류
        tab1, tab2, tab3, tab4 = st.tabs(["📋 기본 정보", "🎬 영상/사진", "📝 신고 양식", "💾 내보내기"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**이벤트 타입:**", event["event_type"])
                st.write("**위반 유형:**", event["violation_type"])
                st.write("**발생 시간:**", event["timestamp"])
                st.write("**위험도:**", event["risk_level"])
            with col2:
                st.write("**차량 번호:**", event["vehicle_number"])
                st.write("**발생 일자:**", event["date"])
                st.write("**발생 시각:**", event["time"])
                st.write("**발생 지역:**", event["location"])
        
        with tab2:
            st.subheader("영상 클립")
            if event.get("video_clip_path"):
                st.video(event["video_clip_path"])
            else:
                st.info("영상 클립이 생성되면 여기에 표시됩니다.")
            
            st.subheader("사진")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**핵심 프레임**")
                if event["images"]["key_frame"]:
                    st.image(event["images"]["key_frame"])
                else:
                    st.info("사진이 생성되면 여기에 표시됩니다.")
            with col2:
                st.write("**차량 Crop**")
                if event["images"]["vehicle_crop"]:
                    st.image(event["images"]["vehicle_crop"])
                else:
                    st.info("사진이 생성되면 여기에 표시됩니다.")
            with col3:
                st.write("**번호판 Crop**")
                if event["images"]["license_plate_crop"]:
                    st.image(event["images"]["license_plate_crop"])
                else:
                    st.info("사진이 생성되면 여기에 표시됩니다.")
        
        with tab3:
            st.subheader("안전신문고 신고 양식")
            report_data = format_report_data(event, user_info)
            
            # 인증번호 입력 (사용자 입력 필요)
            auth_code = st.text_input(
                "인증번호",
                key=f"auth_{event['event_id']}",
                placeholder="인증번호를 입력하세요"
            )
            user_info["auth_code"] = auth_code
            report_data["10. 인증번호"] = auth_code
            
            # 신고 양식 미리보기
            st.json(report_data)
            
            # 제목과 신고 내용 수정 가능
            st.subheader("제목 및 신고 내용 수정")
            edited_title = st.text_input(
                "제목",
                value=event["title"],
                key=f"title_{event['event_id']}",
                max_chars=150
            )
            edited_content = st.text_area(
                "신고 내용",
                value=event["content"],
                key=f"content_{event['event_id']}",
                max_chars=1600,
                height=200
            )
        
        with tab4:
            st.subheader("신고 양식 내보내기")
            
            # JSON 다운로드
            report_json = json.dumps(report_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON 다운로드",
                data=report_json,
                file_name=f"report_event_{event['event_id']}.json",
                mime="application/json"
            )
            
            # CSV 다운로드
            report_df = pd.DataFrame([report_data])
            csv = report_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"report_event_{event['event_id']}.csv",
                mime="text/csv"
            )


def filter_and_sort_events(events: List[Dict], risk_filter: List[str], sort_option: str) -> List[Dict]:
    """이벤트 필터링 및 정렬"""
    # 위험도 필터
    filtered = [e for e in events if e.get("risk_level") in risk_filter]
    
    # 정렬
    if sort_option == "시간순":
        filtered.sort(key=lambda x: x.get("timestamp", ""))
    elif sort_option == "위험도순":
        risk_order = {"높음": 3, "중간": 2, "낮음": 1}
        filtered.sort(key=lambda x: risk_order.get(x.get("risk_level", "낮음"), 0), reverse=True)
    elif sort_option == "이벤트 타입순":
        filtered.sort(key=lambda x: x.get("event_type", ""))
    
    return filtered


# ============================================================================
# 메인 앱 로직
# ============================================================================

def main():
    st.title("🚗 교통 위반 신고 자동화 시스템")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        use_llm, api_key = render_llm_option()
        st.markdown("---")
        st.caption("프로토타입 버전 v0.1")
    
    # 사용자 입력 섹션
    video_file, user_info = render_user_input_section()
    
    st.markdown("---")
    
    # 분석 시작 버튼
    if video_file:
        if st.button("🔍 분석 시작", type="primary", use_container_width=True):
            # 이벤트 검출 (서버 연결 시도, 실패 시 더미 데이터)
            events = detect_events(video_file, user_info)
            
            # 세션 상태에 저장
            st.session_state['events'] = events
            st.session_state['user_info'] = user_info
            st.session_state['video_uploaded'] = True
            
            if events:
                st.success(f"✅ 분석 완료! {len(events)}개의 위반 이벤트가 검출되었습니다.")
            else:
                st.warning("⚠️ 검출된 이벤트가 없습니다.")
            
            st.rerun()
    
    # 검출 결과 표시
    if 'events' in st.session_state and st.session_state.get('video_uploaded', False):
        events = st.session_state['events']
        user_info = st.session_state.get('user_info', {})
        
        # 요약 섹션
        risk_filter, sort_option = render_event_summary(events)
        
        st.markdown("---")
        
        # 필터링 및 정렬
        filtered_events = filter_and_sort_events(events, risk_filter, sort_option)
        
        # 이벤트 목록
        st.header("🔍 검출된 이벤트 목록")
        
        if not filtered_events:
            st.warning("선택한 필터 조건에 맞는 이벤트가 없습니다.")
        else:
            for event in filtered_events:
                render_event_details(event, user_info, use_llm, api_key)
                st.markdown("---")
            
            # 일괄 다운로드
            st.subheader("📦 일괄 다운로드")
            all_reports = []
            for event in filtered_events:
                report_data = format_report_data(event, user_info)
                all_reports.append(report_data)
            
            if all_reports:
                # JSON과 CSV 다운로드 버튼을 나란히 배치
                download_col1, download_col2 = st.columns(2)
                
                with download_col1:
                    # JSON 다운로드
                    json_all = json.dumps(all_reports, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📥 모든 신고 양식 JSON 다운로드",
                        data=json_all,
                        file_name="all_reports.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with download_col2:
                    # CSV 다운로드
                    all_reports_df = pd.DataFrame(all_reports)
                    csv_all = all_reports_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 모든 신고 양식 CSV 다운로드",
                        data=csv_all,
                        file_name="all_reports.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    
    else:
        # 초기 화면 안내
        st.info("👆 위에서 영상을 업로드하고 '분석 시작' 버튼을 클릭하세요.")


if __name__ == "__main__":
    main()
