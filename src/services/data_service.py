"""
데이터 수집 및 처리 서비스
외부 API에서 데이터를 수집하고 가공하는 기능을 제공합니다.
"""
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

from src.config.settings import settings
from src.database.connection import db_manager
from src.database.models import ConsensusReport, StockInfo, RatingEnum
from src.services.vector_service import vector_service

logger = logging.getLogger(__name__)

class DataCollectionService:
    """데이터 수집 서비스"""
    
    def __init__(self):
        self.http_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """HTTP 클라이언트를 초기화합니다."""
        self.http_client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            limits=httpx.Limits(max_connections=settings.max_concurrent_requests)
        )
    
    async def close(self):
        """HTTP 클라이언트를 종료합니다."""
        if self.http_client:
            await self.http_client.aclose()
    
    def normalize_rating(self, rating_raw: str) -> RatingEnum:
        """투자등급을 정규화합니다."""
        rating_lower = rating_raw.lower()
        
        # 매수 등급
        if any(keyword in rating_lower for keyword in ['buy', '매수', 'strong buy', '적극매수']):
            return RatingEnum.buy
        
        # 매도 등급
        elif any(keyword in rating_lower for keyword in ['sell', '매도', 'strong sell', '적극매도']):
            return RatingEnum.sell
        
        # 보유 등급 (기본값)
        else:
            return RatingEnum.hold
    
    async def collect_sample_consensus_data(self) -> List[Dict[str, Any]]:
        """샘플 컨센서스 데이터를 생성합니다. (실제 환경에서는 외부 API 호출)"""
        # 실제 환경에서는 여기서 외부 API를 호출하여 데이터를 수집
        # 현재는 시연용 샘플 데이터를 생성합니다.
        
        sample_data = [
            {
                'stock_code': '005930',  # 삼성전자
                'security_firm': '미래에셋증권',
                'rating_raw': 'Buy',
                'target_price': 85000,
                'report_date': '2024-01-15',
                'analysis_content': '삼성전자는 메모리 반도체 업황 회복과 함께 견조한 실적이 예상됩니다.'
            },
            {
                'stock_code': '000660',  # SK하이닉스
                'security_firm': '삼성증권',
                'rating_raw': 'Strong Buy',
                'target_price': 150000,
                'report_date': '2024-01-16',
                'analysis_content': 'AI 수요 증가로 HBM 메모리 수요가 급증하고 있어 긍정적입니다.'
            },
            {
                'stock_code': '035420',  # NAVER
                'security_firm': 'NH투자증권',
                'rating_raw': 'Hold',
                'target_price': 200000,
                'report_date': '2024-01-17',
                'analysis_content': '커머스 사업 성장은 지속되나 경쟁 심화로 수익성 개선이 필요합니다.'
            }
        ]
        
        return sample_data
    
    async def save_consensus_report(self, report_data: Dict[str, Any]) -> Optional[int]:
        """컨센서스 리포트를 저장합니다."""
        try:
            with db_manager.get_session() as session:
                # 중복 체크
                existing = session.query(ConsensusReport).filter(
                    ConsensusReport.stock_code == report_data['stock_code'],
                    ConsensusReport.security_firm == report_data['security_firm'],
                    ConsensusReport.report_date == datetime.strptime(
                        report_data['report_date'], '%Y-%m-%d'
                    ).date()
                ).first()
                
                if existing:
                    logger.info(f"이미 존재하는 리포트: {report_data['stock_code']}")
                    return existing.id
                
                # 새 리포트 생성
                new_report = ConsensusReport(
                    stock_code=report_data['stock_code'],
                    security_firm=report_data['security_firm'],
                    rating_raw=report_data['rating_raw'],
                    rating_norm=self.normalize_rating(report_data['rating_raw']),
                    target_price=Decimal(str(report_data['target_price'])),
                    report_date=datetime.strptime(
                        report_data['report_date'], '%Y-%m-%d'
                    ).date()
                )
                
                session.add(new_report)
                session.commit()
                session.refresh(new_report)
                
                # 벡터 임베딩 생성 및 저장
                if 'analysis_content' in report_data:
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        vector_service.save_embedding,
                        new_report.id,
                        report_data['analysis_content']
                    )
                
                logger.info(f"새 리포트 저장 완료: ID={new_report.id}")
                return new_report.id
        
        except Exception as e:
            logger.error(f"리포트 저장 실패: {e}")
            return None
    
    async def collect_and_process_data(self) -> Dict[str, Any]:
        """데이터 수집 및 처리를 실행합니다."""
        try:
            logger.info("데이터 수집 시작")
            
            # 샘플 데이터 수집
            sample_data = await self.collect_sample_consensus_data()
            
            processed_count = 0
            failed_count = 0
            
            for report_data in sample_data:
                report_id = await self.save_consensus_report(report_data)
                if report_id:
                    processed_count += 1
                else:
                    failed_count += 1
            
            result = {
                'status': 'completed',
                'processed_count': processed_count,
                'failed_count': failed_count,
                'total_count': len(sample_data),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"데이터 수집 완료: {result}")
            return result
        
        except Exception as e:
            logger.error(f"데이터 수집 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_consensus_summary(self, stock_code: str) -> Dict[str, Any]:
        """특정 종목의 컨센서스 요약을 반환합니다."""
        try:
            with db_manager.get_session() as session:
                reports = session.query(ConsensusReport).filter(
                    ConsensusReport.stock_code == stock_code
                ).all()
                
                if not reports:
                    return {'error': f'종목코드 {stock_code}에 대한 리포트를 찾을 수 없습니다.'}
                
                # 등급별 집계
                rating_counts = {'buy': 0, 'hold': 0, 'sell': 0}
                target_prices = []
                latest_date = None
                
                for report in reports:
                    rating_counts[report.rating_norm.value] += 1
                    target_prices.append(float(report.target_price))
                    if not latest_date or report.report_date > latest_date:
                        latest_date = report.report_date
                
                # 통계 계산
                avg_target_price = sum(target_prices) / len(target_prices) if target_prices else 0
                
                return {
                    'stock_code': stock_code,
                    'total_reports': len(reports),
                    'rating_distribution': rating_counts,
                    'average_target_price': round(avg_target_price, 2),
                    'latest_report_date': latest_date.isoformat() if latest_date else None,
                    'report_count': len(reports)
                }
        
        except Exception as e:
            logger.error(f"컨센서스 요약 조회 실패: {e}")
            return {'error': str(e)}

# 싱글톤 데이터 수집 서비스
data_service = DataCollectionService()