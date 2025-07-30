"""
애플리케이션 초기화 스크립트
데이터베이스 테이블 및 초기 데이터를 설정합니다.
"""
import os
import logging
import asyncio
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

from src.config.settings import settings
from src.database.connection import db_manager
from src.services.data_service import data_service

# 로깅 설정
settings.setup_logging()
logger = logging.getLogger(__name__)

def create_database_schema():
    """데이터베이스 스키마를 생성합니다."""
    try:
        logger.info("데이터베이스 스키마 생성 시작")
        db_manager.create_tables()
        logger.info("데이터베이스 스키마 생성 완료")
    except Exception as e:
        logger.error(f"데이터베이스 스키마 생성 실패: {e}")
        raise

async def collect_initial_data():
    """초기 데이터를 수집합니다."""
    try:
        logger.info("초기 데이터 수집 시작")
        result = await data_service.collect_and_process_data()
        logger.info(f"초기 데이터 수집 완료: {result}")
    except Exception as e:
        logger.error(f"초기 데이터 수집 실패: {e}")
        raise

async def initialize_app():
    """애플리케이션을 초기화합니다."""
    try:
        logger.info("=" * 50)
        logger.info("애플리케이션 초기화 시작")
        logger.info("=" * 50)
        
        # 1. 데이터베이스 스키마 생성
        create_database_schema()
        
        # 2. 초기 데이터 수집
        await collect_initial_data()
        
        # 3. 데이터베이스 연결 테스트
        is_healthy = await db_manager.health_check()
        if not is_healthy:
            raise RuntimeError("데이터베이스 연결 실패")
        
        logger.info("=" * 50)
        logger.info("애플리케이션 초기화 완료")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"애플리케이션 초기화 실패: {e}")
        return False
    finally:
        await data_service.close()

def main():
    """메인 실행 함수"""
    print("증시 투자 애널리스트 AI 서비스 초기화")
    print("=" * 50)
    
    # 환경변수 확인
    if not os.getenv("DB_NAME"):
        print("오류: 환경변수가 설정되지 않았습니다.")
        print(".env 파일을 확인하거나 환경변수를 설정해주세요.")
        return False
    
    # 비동기 초기화 실행
    try:
        result = asyncio.run(initialize_app())
        if result:
            print("\n✅ 초기화가 성공적으로 완료되었습니다!")
            print("다음 명령어로 서버를 시작할 수 있습니다:")
            print("python main.py")
        else:
            print("\n❌ 초기화에 실패했습니다.")
        return result
    except KeyboardInterrupt:
        print("\n초기화가 사용자에 의해 중단되었습니다.")
        return False
    except Exception as e:
        print(f"\n초기화 중 예상치 못한 오류가 발생했습니다: {e}")
        return False

if __name__ == "__main__":
    main()