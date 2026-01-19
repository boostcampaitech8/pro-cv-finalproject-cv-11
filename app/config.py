from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """애플리케이션 설정"""
    
    # 데이터베이스
    db_url: str = Field(default="sqlite:///./app/db.sqlite3", env="DB_URL")
    
    # 모델 경로 (향후 사용)
    model_path: str = Field(default="./model", env="MODEL_PATH")
    
    # 스토리지 경로 (상대 경로)
    storage_base_path: str = Field(default="storage", env="STORAGE_BASE_PATH")
    dummy_plate_images_path: str = Field(
        default="storage/dummy_plate_images",
        env="DUMMY_PLATE_IMAGES_PATH"
    )
    
    # 프로젝트 루트 경로
    project_root: Path = Path(__file__).parent.parent
    
    # 환경 설정
    app_env: str = Field(default="local", env="APP_ENV")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


config = Config()

