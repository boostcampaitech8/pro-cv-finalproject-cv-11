from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlmodel import SQLModel

from config import config
from database import engine
from dependencies import load_model
from api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 데이터베이스 테이블 생성
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)
    
    # 모델 로드
    logger.info("Loading model")
    load_model(config.model_path)
    
    yield
    
    # 종료 시 정리 작업 (필요시)
    logger.info("Shutting down")


app = FastAPI(
    title="교통 위반 신고 자동화 시스템 API",
    description="블랙박스 영상에서 교통 위반 이벤트를 자동으로 추출하는 API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(router, prefix="/api/v1", tags=["api"])


@app.get("/")
def root():
    """루트 엔드포인트"""
    return {"message": "교통 위반 신고 자동화 시스템 API", "version": "0.1.0"}


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

