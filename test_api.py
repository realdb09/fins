"""
API 테스트 스크립트
주요 API 엔드포인트들의 동작을 테스트합니다.
"""
import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:2400/api/v1"  # 포트 2400으로 변경

async def test_health_check():
    """헬스체크 테스트"""
    print("🔍 헬스체크 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   상태코드: {response.status_code}")
            print(f"   응답: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"   오류: {e}")
            return False

async def test_data_collection():
    """데이터 수집 테스트"""
    print("📊 데이터 수집 테스트...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/data/collect")
            print(f"   상태코드: {response.status_code}")
            print(f"   응답: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"   오류: {e}")
            return False

async def test_consensus_query():
    """컨센서스 조회 테스트"""
    print("📈 컨센서스 조회 테스트...")
    stock_code = "005930"  # 삼성전자
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/consensus/{stock_code}")
            print(f"   상태코드: {response.status_code}")
            result = response.json()
            if response.status_code == 200:
                print(f"   종목코드: {result.get('stock_code')}")
                print(f"   리포트 수: {result.get('total_reports')}")
                print(f"   평균 목표가: {result.get('average_target_price')}")
            else:
                print(f"   응답: {result}")
            return response.status_code == 200
        except Exception as e:
            print(f"   오류: {e}")
            return False

async def test_stock_analysis():
    """AI 종목 분석 테스트"""
    print("🤖 AI 종목 분석 테스트...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {"stock_code": "005930"}
            response = await client.post(
                f"{BASE_URL}/analysis/stock",
                json=payload
            )
            print(f"   상태코드: {response.status_code}")
            result = response.json()
            if response.status_code == 200:
                print(f"   종목코드: {result.get('stock_code')}")
                ai_analysis = result.get('ai_analysis', {})
                print(f"   AI 투자의견: {ai_analysis.get('investment_opinion')}")
                print(f"   신뢰도: {ai_analysis.get('confidence_level')}")
            else:
                print(f"   응답: {result}")
            return response.status_code == 200
        except Exception as e:
            print(f"   오류: {e}")
            return False

async def test_vector_search():
    """벡터 검색 테스트"""
    print("🔍 벡터 검색 테스트...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "query": "삼성전자 투자 전망",
                "limit": 5
            }
            response = await client.post(
                f"{BASE_URL}/search",
                json=payload
            )
            print(f"   상태코드: {response.status_code}")
            result = response.json()
            if response.status_code == 200:
                print(f"   검색어: {result.get('query')}")
                print(f"   결과 수: {len(result.get('results', []))}")
                print(f"   관련 종목: {result.get('related_stocks', [])}")
            else:
                print(f"   응답: {result}")
            return response.status_code == 200
        except Exception as e:
            print(f"   오류: {e}")
            return False

async def test_stock_list():
    """종목 목록 테스트"""
    print("📋 종목 목록 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/stocks?limit=10")
            print(f"   상태코드: {response.status_code}")
            result = response.json()
            if response.status_code == 200:
                print(f"   종목 수: {result.get('count')}")
                print(f"   종목들: {result.get('stocks', [])}")
            else:
                print(f"   응답: {result}")
            return response.status_code == 200
        except Exception as e:
            print(f"   오류: {e}")
            return False

async def run_all_tests():
    """모든 테스트 실행"""
    print("🧪 API 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("헬스체크", test_health_check),
        ("데이터 수집", test_data_collection),
        ("컨센서스 조회", test_consensus_query),
        ("AI 종목 분석", test_stock_analysis),
        ("벡터 검색", test_vector_search),
        ("종목 목록", test_stock_list),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} 테스트 실행:")
        success = await test_func()
        results.append((test_name, success))
        print(f"   결과: {'✅ 성공' if success else '❌ 실패'}")
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약:")
    print("=" * 50)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"   {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n📈 성공률: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 서버 상태를 확인해주세요.")

def main():
    """메인 실행 함수"""
    print("🚀 API 테스트 도구")
    print("서버가 http://localhost:2400에서 실행 중이어야 합니다.")
    print("서버를 먼저 시작하려면: python main.py")
    print()
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n테스트 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()