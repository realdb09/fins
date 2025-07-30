"""
서버 실행 스크립트
개발 및 운영 환경에서 서버를 시작하는 편의 스크립트입니다.
"""
import os
import sys
import argparse
import uvicorn
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

from src.config.settings import settings

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="증시 투자 애널리스트 AI 서비스 서버")
    parser.add_argument("--host", default=settings.api.host, help="호스트 주소")
    parser.add_argument("--port", type=int, default=settings.api.port, help="포트 번호")
    parser.add_argument("--reload", action="store_true", default=settings.api.reload, help="자동 리로드")
    parser.add_argument("--log-level", default=settings.api.log_level, help="로그 레벨")
    parser.add_argument("--workers", type=int, default=1, help="워커 프로세스 수")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 증시 투자 애널리스트 AI 서비스 시작")
    print("=" * 60)
    print(f"📡 서버 주소: http://{args.host}:{args.port}")
    print(f"📊 API 문서: http://{args.host}:{args.port}/docs")
    print(f"🤖 LLM 제공자: {settings.llm.provider}")
    print(f"🔧 리로드: {'활성화' if args.reload else '비활성화'}")
    print(f"📝 로그 레벨: {args.log_level.upper()}")
    print("=" * 60)
    
    try:
        # 환경변수 확인
        if not os.getenv("DB_NAME"):
            print("❌ 오류: 환경변수가 설정되지 않았습니다.")
            print("💡 .env 파일을 확인하거나 init_app.py를 먼저 실행해주세요.")
            sys.exit(1)
        
        # uvicorn 서버 시작
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers if not args.reload else 1
        )
        
    except KeyboardInterrupt:
        print("\n👋 서버가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 시작 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()