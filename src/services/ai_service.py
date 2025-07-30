"""
AI Agent 서비스
다양한 LLM 제공자를 활용한 투자 분석 AI Agent 기능을 제공합니다.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.config.settings import settings
from src.services.data_service import data_service
from src.services.vector_service import vector_service
from src.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class AIAnalysisService:
    """AI 분석 서비스"""
    
    def __init__(self):
        self.llm_config = settings.get_llm_config()
        self.autogen_enabled = settings.autogen.enabled
    
    async def analyze_stock_consensus(self, stock_code: str) -> Dict[str, Any]:
        """종목에 대한 컨센서스 분석을 수행합니다."""
        try:
            logger.info(f"종목 분석 시작: {stock_code}")
            
            # 컨센서스 데이터 수집
            consensus_data = data_service.get_consensus_summary(stock_code)
            
            if 'error' in consensus_data:
                return consensus_data
            
            # 유사 리포트 검색
            similar_reports = vector_service.search_similar_reports(
                query_text=f"종목코드 {stock_code} 투자 분석",
                stock_code=stock_code,
                limit=5
            )
            
            # AI 분석 수행 (실제 환경에서는 LLM 호출)
            analysis_result = await self._generate_investment_insight(
                consensus_data, similar_reports
            )
            
            return {
                'stock_code': stock_code,
                'consensus_summary': consensus_data,
                'similar_reports': similar_reports,
                'ai_analysis': analysis_result,
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"종목 분석 실패: {e}")
            return {'error': str(e)}
    
    async def _generate_investment_insight(
        self, 
        consensus_data: Dict[str, Any], 
        similar_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """투자 인사이트를 생성합니다."""
        try:
            # LLM을 사용한 투자 인사이트 생성
            system_prompt = """
            당신은 전문 투자 애널리스트입니다. 
            제공된 컨센서스 데이터와 유사 리포트를 분석하여 투자 인사이트를 제공해주세요.
            분석은 객관적이고 균형잡힌 관점에서 작성해주세요.
            """
            
            rating_dist = consensus_data.get('rating_distribution', {})
            total_reports = consensus_data.get('total_reports', 0)
            avg_target_price = consensus_data.get('average_target_price', 0)
            
            # 프롬프트 생성
            prompt = f"""
            다음 컨센서스 데이터를 분석해주세요:
            
            전체 리포트 수: {total_reports}개
            투자 등급 분포:
            - 매수: {rating_dist.get('buy', 0)}개
            - 보유: {rating_dist.get('hold', 0)}개  
            - 매도: {rating_dist.get('sell', 0)}개
            
            평균 목표주가: {avg_target_price:,.0f}원
            
            유사 리포트 {len(similar_reports)}개가 참고자료로 제공되었습니다.
            
            다음 형식으로 분석해주세요:
            1. 투자 의견 (Strong Buy/Buy/Hold/Sell 중 하나)
            2. 신뢰도 (High/Medium/Low)
            3. 분석 요약 (3-4문장)
            4. 주요 리스크 요인 (3개)
            5. 주요 기회 요인 (3개)
            """
            
            # LLM 응답 생성
            ai_response = await llm_service.generate_response(prompt, system_prompt)
            
            # 투자 의견 결정
            buy_ratio = rating_dist.get('buy', 0) / total_reports if total_reports > 0 else 0
            sell_ratio = rating_dist.get('sell', 0) / total_reports if total_reports > 0 else 0
            
            if buy_ratio > 0.6:
                investment_opinion = "Strong Buy"
                confidence = "High"
            elif buy_ratio > 0.4:
                investment_opinion = "Buy"
                confidence = "Medium"
            elif sell_ratio > 0.4:
                investment_opinion = "Sell"
                confidence = "Medium"
            else:
                investment_opinion = "Hold"
                confidence = "Low"
            
            # 분석 요약 생성
            summary = ai_response if ai_response else f"""
            전체 {total_reports}개 리포트 분석 결과
            매수 의견 {buy_ratio:.1%}, 평균 목표주가 {avg_target_price:,.0f}원
            AI 종합 의견: {investment_opinion} (신뢰도: {confidence})
            """.strip()
            
            # 주요 리스크 및 기회 요인 (샘플)
            risk_factors = [
                "시장 전반적인 불확실성 증가",
                "업종별 경쟁 심화",
                "거시경제 환경 변화"
            ]
            
            opportunity_factors = [
                "기술 혁신을 통한 시장 점유율 확대",
                "신규 사업 영역 진출",
                "ESG 경영을 통한 지속가능한 성장"
            ]
            
            return {
                'investment_opinion': investment_opinion,
                'confidence_level': confidence,
                'summary': summary,
                'ai_analysis': ai_response,
                'risk_factors': risk_factors,
                'opportunity_factors': opportunity_factors,
                'target_price_consensus': avg_target_price,
                'analyst_count': total_reports
            }
        
        except Exception as e:
            logger.error(f"투자 인사이트 생성 실패: {e}")
            return {'error': str(e)}
    
    async def search_and_analyze(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """검색 쿼리에 대한 분석을 수행합니다."""
        try:
            logger.info(f"검색 분석 시작: {query}")
            
            # 벡터 검색 수행
            similar_reports = vector_service.search_similar_reports(
                query_text=query,
                limit=limit,
                similarity_threshold=0.3
            )
            
            # 검색 결과 분석
            if not similar_reports:
                return {
                    'query': query,
                    'results': [],
                    'analysis': '검색 결과가 없습니다.',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 결과 요약
            stock_codes = list(set([report['stock_code'] for report in similar_reports]))
            avg_similarity = sum([report['similarity_score'] for report in similar_reports]) / len(similar_reports)
            
            # LLM을 사용한 검색 결과 분석
            system_prompt = "당신은 투자 분석 전문가입니다. 검색 결과를 분석하여 투자자에게 유용한 인사이트를 제공해주세요."
            
            prompt = f"""
            검색어: "{query}"
            관련 리포트: {len(similar_reports)}개
            관련 종목: {', '.join(stock_codes)}
            평균 유사도: {avg_similarity:.3f}
            
            이 검색 결과에 대한 투자 관점에서의 분석과 시사점을 제공해주세요.
            """
            
            ai_analysis = await llm_service.generate_response(prompt, system_prompt)
            
            analysis_summary = ai_analysis if ai_analysis else f"""
            검색 쿼리 '{query}'에 대한 분석 결과
            관련 리포트 {len(similar_reports)}개, 관련 종목 {len(stock_codes)}개 발견
            평균 유사도 {avg_similarity:.3f}로 관련성이 높은 자료들입니다.
            """.strip()
            
            return {
                'query': query,
                'results': similar_reports,
                'analysis': analysis_summary,
                'ai_analysis': ai_analysis,
                'related_stocks': stock_codes,
                'average_similarity': avg_similarity,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"검색 분석 실패: {e}")
            return {'error': str(e)}
    
    def get_service_info(self) -> Dict[str, Any]:
        """AI 서비스 정보를 반환합니다."""
        return {
            'llm_provider': llm_service.get_provider_info(),
            'autogen_enabled': self.autogen_enabled,
            'langfuse_enabled': settings.langfuse.enabled,
            'phoenix_enabled': settings.phoenix.enabled
        }

# 싱글톤 AI 분석 서비스
ai_service = AIAnalysisService()