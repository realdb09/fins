"""
데이터베이스 연결 관리
환경변수를 통해 데이터베이스 설정을 주입받아 연결을 관리합니다.
"""
import logging
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.settings import settings
from src.database.models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 연결 관리자"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """데이터베이스 엔진을 초기화합니다."""
        try:
            if settings.database.db_type.lower() == "sqlite":
                # SQLite 설정
                database_url = f"sqlite:///{settings.database.db_name}"
                async_database_url = f"sqlite+aiosqlite:///{settings.database.db_name}"
                
                # 동기 엔진
                self.engine = create_engine(
                    database_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=settings.api.log_level.lower() == "debug"
                )
                
                # 비동기 엔진
                self.async_engine = create_async_engine(
                    async_database_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=settings.api.log_level.lower() == "debug"
                )
                
                # SQLite 설정 최적화
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA cache_size=10000")
                    cursor.execute("PRAGMA temp_store=memory")
                    cursor.close()
            
            else:
                raise ValueError(f"지원하지 않는 데이터베이스 타입: {settings.database.db_type}")
            
            # 세션 팩토리 생성
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info(f"데이터베이스 엔진 초기화 완료: {settings.database.db_type}")
            
        except Exception as e:
            logger.error(f"데이터베이스 엔진 초기화 실패: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """동기 데이터베이스 세션을 반환합니다."""
        if not self.SessionLocal:
            raise RuntimeError("데이터베이스 세션이 초기화되지 않았습니다.")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"데이터베이스 트랜잭션 오류: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """비동기 데이터베이스 세션을 반환합니다."""
        if not self.AsyncSessionLocal:
            raise RuntimeError("비동기 데이터베이스 세션이 초기화되지 않았습니다.")
        
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"비동기 데이터베이스 트랜잭션 오류: {e}")
                raise
    
    def create_tables(self):
        """데이터베이스 테이블을 생성합니다."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("데이터베이스 테이블 생성 완료")
        except Exception as e:
            logger.error(f"테이블 생성 실패: {e}")
            raise
    
    def drop_tables(self):
        """데이터베이스 테이블을 삭제합니다. (개발용)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("데이터베이스 테이블 삭제 완료")
        except Exception as e:
            logger.error(f"테이블 삭제 실패: {e}")
            raise
    
    async def health_check(self) -> bool:
        """데이터베이스 연결 상태를 확인합니다."""
        try:
            async with self.get_async_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"데이터베이스 헬스체크 실패: {e}")
            return False

# 싱글톤 데이터베이스 매니저
db_manager = DatabaseManager()

# 편의 함수들
def get_db_session():
    """데이터베이스 세션을 반환하는 의존성 주입 함수"""
    return db_manager.get_session()

async def get_async_db_session():
    """비동기 데이터베이스 세션을 반환하는 의존성 주입 함수"""
    async with db_manager.get_async_session() as session:
        yield session