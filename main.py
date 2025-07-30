"""
FastAPI 애플리케이션 메인 진입점
"""
import os
import logging
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.config.settings import settings
from src.database.connection import db_manager
from src.services.data_service import data_service
from src.api.routes import router

# 로깅 설정
settings.setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행할 작업"""
    try:
        # 시작 시
        logger.info("애플리케이션 시작 중...")
        
        # 데이터베이스 테이블 생성
        db_manager.create_tables()
        
        # 초기 데이터 수집 (환경변수로 제어)
        if os.getenv("AUTO_COLLECT_DATA", "false").lower() == "true":
            await data_service.collect_and_process_data()
        
        logger.info("애플리케이션 시작 완료")
        yield
        
    except Exception as e:
        logger.error(f"애플리케이션 시작 실패: {e}")
        raise
    finally:
        # 종료 시
        logger.info("애플리케이션 종료 중...")
        await data_service.close()
        logger.info("애플리케이션 종료 완료")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="증시 투자 애널리스트 AI 서비스",
    description="증권사 리포트·컨센서스 데이터를 통합하여 AI 기반 투자 인사이트를 제공하는 서비스",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영환경에서는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router, prefix="/api/v1")

# 루트 경로 리다이렉션
@app.get("/", include_in_schema=False)
async def root():
    """루트 경로에서 API 문서로 리다이렉션"""
    return RedirectResponse(url="/docs")

# 메인 실행
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        log_level=settings.api.log_level
    )