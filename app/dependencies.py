from loguru import logger
from typing import Optional

# TODO: 실제 모델 통합 시 이 부분을 수정
# 현재는 더미 모델 인터페이스만 제공

_model = None


def load_model(model_path: str) -> None:
    """
    모델 로드 함수 (향후 실제 모델 통합 대비)
    
    Args:
        model_path: 모델 파일 경로
    """
    global _model
    logger.info(f"Loading model from {model_path}.")
    
    # TODO: 실제 모델 로드 로직 구현
    # 현재는 더미로 None 설정
    _model = None
    
    logger.info("Model loaded (dummy mode).")


def get_model():
    """
    로드된 모델 반환
    
    Returns:
        모델 객체 (현재는 None)
    """
    global _model
    return _model

