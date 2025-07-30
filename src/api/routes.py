"""
FastAPI 라우터 정의
RESTful API 엔드포인트를 제공합니다.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from src.services.data_service import data_service
from src.services.ai_service import ai_service
from src.services.vector_service import vector_service
from src.database.connection import db_manager

logger = logging.getLogger(__name__)

# 라우터 인스턴스 생성
router = APIRouter()

# Pydantic 모델 정의
class AnalysisRequest(BaseModel):
    """분석 요청 모델"""
    stock_code: str = Field(..., description="종목코드", example="005930")

class SearchRequest(BaseModel):
    """검색 요청 모델"""
    query: str = Field(..., description="검색 쿼리", example="삼성전자 투자 전망")
    limit: int = Field(default=10, ge=1, le=50, description="결과 개수")

class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    timestamp: str
    version: str = "1.0.0"

class ConsensusResponse(BaseModel):
    """컨센서스 응답 모델"""
    stock_code: str
    total_reports: int
    rating_distribution: Dict[str, int]
    average_target_price: float
    latest_report_date: Optional[str]

# 헬스체크 엔드포인트
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """시스템 헬스체크를 수행합니다."""
    try:
        # 데이터베이스 연결 확인
        db_healthy = await db_manager.health_check()
        status = "healthy" if db_healthy else "unhealthy"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"헬스체크 실패: {e}")
        raise HTTPException(status_code=500, detail="시스템 오류가 발생했습니다.")

# 데이터 수집 엔드포인트
@router.post("/data/collect", tags=["Data"])
async def collect_data():
    """컨센서스 데이터를 수집하고 처리합니다."""
    try:
        result = await data_service.collect_and_process_data()
        return result
    except Exception as e:
        logger.error(f"데이터 수집 실패: {e}")
        raise HTTPException(status_code=500, detail=f"데이터 수집 중 오류 발생: {str(e)}")

# 컨센서스 조회 엔드포인트
@router.get("/consensus/{stock_code}", response_model=ConsensusResponse, tags=["Analysis"])
async def get_consensus(stock_code: str):
    """특정 종목의 컨센서스 정보를 조회합니다."""
    try:
        result = data_service.get_consensus_summary(stock_code)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return ConsensusResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"컨센서스 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="컨센서스 조회 중 오류 발생")

# AI 분석 엔드포인트
@router.post("/analysis/stock", tags=["Analysis"])
async def analyze_stock(request: AnalysisRequest):
    """종목에 대한 AI 분석을 수행합니다."""
    try:
        result = await ai_service.analyze_stock_consensus(request.stock_code)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"종목 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="종목 분석 중 오류 발생")

# 벡터 검색 엔드포인트
@router.post("/search", tags=["Search"])
async def search_reports(request: SearchRequest):
    """벡터 검색을 통해 유사한 리포트를 찾습니다."""
    try:
        result = await ai_service.search_and_analyze(request.query, request.limit)
        return result
    except Exception as e:
        logger.error(f"검색 실패: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류 발생")

# AI 서비스 정보 엔드포인트
@router.get("/ai/info", tags=["System"])
async def get_ai_info():
    """AI 서비스 정보를 조회합니다."""
    try:
        info = ai_service.get_service_info()
        return info
    except Exception as e:
        logger.error(f"AI 서비스 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="AI 서비스 정보 조회 중 오류 발생")

# 벡터 서비스 통계 엔드포인트
@router.get("/vector/stats", tags=["System"])
async def get_vector_stats():
    """벡터 임베딩 통계 정보를 조회합니다."""
    try:
        stats = vector_service.get_embedding_stats()
        return stats
    except Exception as e:
        logger.error(f"벡터 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="통계 조회 중 오류 발생")

# 종목 목록 엔드포인트
@router.get("/stocks", tags=["Data"])
async def get_stock_list(
    limit: int = Query(default=50, ge=1, le=200, description="결과 개수"),
    offset: int = Query(default=0, ge=0, description="시작 위치")
):
    """등록된 종목 목록을 조회합니다."""
    try:
        with db_manager.get_session() as session:
            from src.database.models import ConsensusReport
            
            # 중복 제거하여 종목 목록 조회
            query = session.query(
                ConsensusReport.stock_code
            ).distinct().offset(offset).limit(limit)
            
            results = query.all()
            stock_codes = [row.stock_code for row in results]
            
            return {
                'stocks': stock_codes,
                'count': len(stock_codes),
                'offset': offset,
                'limit': limit
            }
    except Exception as e:
        logger.error(f"종목 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="종목 목록 조회 중 오류 발생")

# 최근 리포트 엔드포인트
@router.get("/reports/recent", tags=["Data"])
async def get_recent_reports(
    limit: int = Query(default=20, ge=1, le=100, description="결과 개수"),
    stock_code: Optional[str] = Query(default=None, description="종목코드 필터")
):
    """최근 리포트 목록을 조회합니다."""
    try:
        with db_manager.get_session() as session:
            from src.database.models import ConsensusReport
            
            query = session.query(ConsensusReport)
            
            if stock_code:
                query = query.filter(ConsensusReport.stock_code == stock_code)
            
            query = query.order_by(ConsensusReport.created_at.desc()).limit(limit)
            results = query.all()
            
            reports = []
            for report in results:
                reports.append({
                    'id': report.id,
                    'stock_code': report.stock_code,
                    'security_firm': report.security_firm,
                    'rating_raw': report.rating_raw,
                    'rating_norm': report.rating_norm.value,
                    'target_price': float(report.target_price),
                    'report_date': report.report_date.isoformat(),
                    'created_at': report.created_at.isoformat()
                })
            
            return {
                'reports': reports,
                'count': len(reports),
                'limit': limit
            }
    except Exception as e:
        logger.error(f"최근 리포트 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="리포트 조회 중 오류 발생")