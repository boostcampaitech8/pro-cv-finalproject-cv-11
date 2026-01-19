from typing import Dict
from loguru import logger


def generate_title_and_content(
    event_type: str,
    violation_type: str,
    provider: str,
    api_key: str = None
) -> Dict[str, str]:
    """
    LLM을 사용하여 제목과 신고 내용 생성 (현재는 더미 템플릿)
    
    Args:
        event_type: 위반 이벤트 유형 (0번 항목)
        violation_type: 자동차·교통 위반 신고 유형 (1번 항목)
        provider: LLM 제공자 (사용 안 함/OpenAI/Anthropic/Google)
        api_key: LLM API 키 (선택)
    
    Returns:
        {"title": "...", "content": "..."}
    """
    # TODO: 실제 LLM API 호출 구현
    # 현재는 더미 템플릿 사용
    
    if provider == "사용 안 함" or not provider:
        # 기본 템플릿
        title = f"{event_type} 위반 차량 신고"
        content = f"해당 차량이 {event_type} 위반을 저질렀습니다. 상세 내용은 첨부된 영상과 사진을 참고해주세요."
    else:
        # 향후 LLM API 호출
        logger.info(f"LLM 사용 예정: {provider} (아직 구현되지 않음)")
        title = f"{event_type} 위반 차량 신고"
        content = f"해당 차량이 {event_type} 위반을 저질렀습니다. 상세 내용은 첨부된 영상과 사진을 참고해주세요."
    
    return {
        "title": title,
        "content": content
    }

