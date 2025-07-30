"""
데이터베이스 모델 정의
SQLAlchemy를 사용하여 MariaDB 스키마를 SQLite로 호환되도록 구현
"""
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, DECIMAL, 
    Date, DateTime, Enum, LargeBinary, Index,
    create_engine, MetaData
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import enum
from datetime import datetime, date
from typing import Optional

Base = declarative_base()

class RatingEnum(enum.Enum):
    """투자 등급 열거형"""
    buy = "buy"
    hold = "hold"
    sell = "sell"

class ConsensusReport(Base):
    """컨센서스 리포트 테이블"""
    __tablename__ = "consensus_reports"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, comment="종목코드")
    security_firm = Column(String(120), nullable=False, comment="증권사명")
    rating_raw = Column(String(64), nullable=False, comment="원본 투자등급")
    rating_norm = Column(Enum(RatingEnum), nullable=False, comment="정규화된 투자등급")
    target_price = Column(DECIMAL(15, 2), nullable=False, comment="목표주가")
    report_date = Column(Date, nullable=False, comment="리포트 날짜")
    created_at = Column(DateTime, default=func.now(), comment="생성일시")
    
    # 복합 유니크 인덱스 (stock_code, security_firm, report_date)
    __table_args__ = (
        Index('uk_report', 'stock_code', 'security_firm', 'report_date', unique=True),
        Index('idx_stock_code', 'stock_code'),
        Index('idx_report_date', 'report_date'),
        Index('idx_rating_norm', 'rating_norm'),
    )

class VectorEmbedding(Base):
    """벡터 임베딩 테이블"""
    __tablename__ = "vector_embeddings"
    
    report_id = Column(BigInteger, primary_key=True, comment="리포트 ID (FK)")
    embedding = Column(LargeBinary, nullable=False, comment="벡터 임베딩 데이터")
    
    __table_args__ = (
        Index('idx_vector', 'report_id'),
    )

class StockInfo(Base):
    """종목 정보 테이블"""
    __tablename__ = "stock_info"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), unique=True, nullable=False, comment="종목코드")
    stock_name = Column(String(100), nullable=False, comment="종목명")
    market_type = Column(String(20), nullable=False, comment="시장구분 (KOSPI/KOSDAQ)")
    sector = Column(String(50), comment="업종")
    market_cap = Column(BigInteger, comment="시가총액")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_stock_code', 'stock_code'),
        Index('idx_market_type', 'market_type'),
        Index('idx_sector', 'sector'),
    )

class AnalysisResult(Base):
    """AI 분석 결과 테이블"""
    __tablename__ = "analysis_results"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, comment="종목코드")
    analysis_type = Column(String(50), nullable=False, comment="분석유형")
    analysis_content = Column(Text, nullable=False, comment="분석내용")
    confidence_score = Column(DECIMAL(5, 4), comment="신뢰도 점수")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_stock_analysis', 'stock_code', 'analysis_type'),
        Index('idx_created_at', 'created_at'),
    )

# 데이터베이스 메타데이터
metadata = MetaData()