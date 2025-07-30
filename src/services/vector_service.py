"""
벡터 검색 서비스
문서 임베딩 생성 및 유사도 검색 기능을 제공합니다.
"""
import logging
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.config.settings import settings
from src.database.connection import db_manager
from src.database.models import VectorEmbedding, ConsensusReport

logger = logging.getLogger(__name__)

class VectorSearchService:
    """벡터 검색 서비스"""
    
    def __init__(self):
        self.model = None
        self.dimension = settings.vector.dimension
        self.model_name = settings.vector.model
        self._initialize_model()
    
    def _initialize_model(self):
        """SentenceTransformer 모델을 초기화합니다."""
        try:
            logger.info(f"벡터 모델 로딩 시작: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("벡터 모델 로딩 완료")
        except Exception as e:
            logger.error(f"벡터 모델 로딩 실패: {e}")
            # 기본 모델로 폴백
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("기본 벡터 모델로 폴백 완료")
            except Exception as fallback_error:
                logger.error(f"기본 모델 로딩도 실패: {fallback_error}")
                raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """텍스트에 대한 벡터 임베딩을 생성합니다."""
        try:
            if not self.model:
                raise RuntimeError("벡터 모델이 초기화되지 않았습니다.")
            
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.astype(np.float32)
        
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {e}")
            raise
    
    def batch_generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """여러 텍스트에 대한 벡터 임베딩을 배치로 생성합니다."""
        try:
            if not self.model:
                raise RuntimeError("벡터 모델이 초기화되지 않았습니다.")
            
            embeddings = self.model.encode(texts, normalize_embeddings=True, batch_size=32)
            return embeddings.astype(np.float32)
        
        except Exception as e:
            logger.error(f"배치 임베딩 생성 실패: {e}")
            raise
    
    def save_embedding(self, report_id: int, text: str) -> bool:
        """리포트의 임베딩을 생성하고 저장합니다."""
        try:
            embedding = self.generate_embedding(text)
            embedding_blob = pickle.dumps(embedding)
            
            with db_manager.get_session() as session:
                # 기존 임베딩이 있는지 확인
                existing = session.query(VectorEmbedding).filter(
                    VectorEmbedding.report_id == report_id
                ).first()
                
                if existing:
                    existing.embedding = embedding_blob
                else:
                    new_embedding = VectorEmbedding(
                        report_id=report_id,
                        embedding=embedding_blob
                    )
                    session.add(new_embedding)
                
                session.commit()
                logger.info(f"임베딩 저장 완료: report_id={report_id}")
                return True
        
        except Exception as e:
            logger.error(f"임베딩 저장 실패: {e}")
            return False
    
    def search_similar_reports(
        self, 
        query_text: str, 
        limit: int = 10, 
        similarity_threshold: float = 0.5,
        stock_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """유사한 리포트를 검색합니다."""
        try:
            query_embedding = self.generate_embedding(query_text)
            
            with db_manager.get_session() as session:
                # 임베딩과 리포트 정보를 조인하여 조회
                query = session.query(
                    VectorEmbedding, ConsensusReport
                ).join(
                    ConsensusReport, VectorEmbedding.report_id == ConsensusReport.id
                )
                
                # 종목 필터링
                if stock_code:
                    query = query.filter(ConsensusReport.stock_code == stock_code)
                
                results = query.all()
                
                # 유사도 계산 및 정렬
                similarities = []
                for embedding_row, report_row in results:
                    stored_embedding = pickle.loads(embedding_row.embedding)
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        stored_embedding.reshape(1, -1)
                    )[0][0]
                    
                    if similarity >= similarity_threshold:
                        similarities.append({
                            'report_id': report_row.id,
                            'stock_code': report_row.stock_code,
                            'security_firm': report_row.security_firm,
                            'rating_norm': report_row.rating_norm.value,
                            'target_price': float(report_row.target_price),
                            'report_date': report_row.report_date.isoformat(),
                            'similarity_score': float(similarity)
                        })
                
                # 유사도 순으로 정렬
                similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
                
                return similarities[:limit]
        
        except Exception as e:
            logger.error(f"유사 리포트 검색 실패: {e}")
            return []
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """임베딩 통계 정보를 반환합니다."""
        try:
            with db_manager.get_session() as session:
                total_embeddings = session.query(VectorEmbedding).count()
                
                return {
                    'total_embeddings': total_embeddings,
                    'model_name': self.model_name,
                    'dimension': self.dimension,
                    'model_loaded': self.model is not None
                }
        
        except Exception as e:
            logger.error(f"임베딩 통계 조회 실패: {e}")
            return {'error': str(e)}

# 싱글톤 벡터 검색 서비스
vector_service = VectorSearchService()