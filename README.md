# 증시 투자 애널리스트 AI 서비스

증권사 리포트·컨센서스 데이터를 통합 수집·가공하여 AI Agent 기반 투자 인사이트를 생성·제공하는 서비스입니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Frontend      │    │    Backend API       │    │   AI Services       │
│   (React)       │◄──►│   (FastAPI)          │◄──►│   (LangChain)       │
│   Port: 3000    │    │   Port: 8000         │    │   Vector Search     │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                │
                                ▼
                       ┌─────────────────────┐
                       │   Database Layer    │
                       │   (SQLite/SQLAlchemy)│
                       │   Vector Embeddings │
                       └─────────────────────┘
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# Python 가상환경 생성 (Python 3.10.18 권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 편집하여 필요한 설정값 입력 (최소 필수 항목):
# - LLM_PROVIDER: 사용할 LLM 제공자 (openai, google, ollama, deepinfra)
# - 해당 제공자의 API 키 설정
# - MARIADB_* : 데이터베이스 연결 정보 (또는 SQLite 사용)
```

### 3. 애플리케이션 초기화

```bash
# 데이터베이스 및 초기 데이터 설정
python init_app.py
```

### 4. 백엔드 서버 실행 (포트 2400)

```bash
# 개발 서버 시작
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 2400 --reload

# 또는 실행 스크립트 사용
python run_server.py --reload
```

### 5. 프론트엔드 서버 실행 (포트 2300)

```bash
# 프론트엔드 개발 서버 시작
npm run dev
# 또는
npm run dev:frontend
```

### 6. API 문서 확인

브라우저에서 다음 URL을 열어 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:2400/docs
- ReDoc: http://localhost:2400/redoc
- 프론트엔드: http://localhost:2300

## 📁 프로젝트 구조

```
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # 환경변수 기반 설정 관리
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy 모델 정의
│   │   └── connection.py        # 데이터베이스 연결 관리
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py      # 데이터 수집 및 처리
│   │   ├── vector_service.py    # 벡터 검색 서비스
│   │   ├── ai_service.py        # AI 분석 서비스
│   │   └── llm_service.py       # LLM 통합 서비스
│   └── api/
│       ├── __init__.py
│       └── routes.py            # FastAPI 라우터
├── main.py                      # 애플리케이션 진입점
├── init_app.py                  # 초기화 스크립트
├── run_server.py                # 서버 실행 스크립트
├── test_api.py                  # API 테스트 도구
├── requirements.txt             # Python 의존성
├── .env.example                 # 환경변수 템플릿
└── README.md
```

## 🔧 주요 기능

### 1. 다중 LLM 제공자 지원
- OpenAI GPT 모델
- Google Gemini 모델  
- Ollama 로컬 모델
- DeepInfra 모델
- 환경변수를 통한 동적 제공자 변경

### 2. 데이터 수집 및 관리
- 증권사 컨센서스 리포트 데이터 수집
- 투자등급 정규화 (Buy/Hold/Sell)
- 벡터 임베딩을 통한 유사도 검색

### 3. AI 분석 서비스
- 종목별 컨센서스 분석
- 투자 인사이트 생성
- 리스크 및 기회 요인 분석

### 4. RESTful API
- `/api/v1/health` - 시스템 헬스체크
- `/api/v1/data/collect` - 데이터 수집
- `/api/v1/consensus/{stock_code}` - 컨센서스 조회
- `/api/v1/analysis/stock` - AI 종목 분석
- `/api/v1/search` - 벡터 검색
- `/api/v1/ai/info` - AI 서비스 정보
- `/api/v1/stocks` - 종목 목록
- `/api/v1/reports/recent` - 최근 리포트

## 🔍 API 사용 예제

### 1. 데이터 수집
```bash
curl -X POST "http://localhost:2400/api/v1/data/collect"
```

### 2. 종목 컨센서스 조회
```bash
curl "http://localhost:2400/api/v1/consensus/005930"
```

### 3. AI 종목 분석
```bash
curl -X POST "http://localhost:2400/api/v1/analysis/stock" \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "005930"}'
```

### 4. 벡터 검색
```bash
curl -X POST "http://localhost:2400/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "삼성전자 투자 전망", "limit": 10}'
```

### 5. AI 서비스 정보 조회
```bash
curl "http://localhost:2400/api/v1/ai/info"
```

## ⚙️ 환경변수 설정

주요 환경변수들:

| 구분 | 변수명 | 설명 | 기본값 |
|------|--------|------|--------|
| LLM | `LLM_PROVIDER` | LLM 제공자 | `openai` |
| LLM | `OPENAI_API_KEY` | OpenAI API 키 | - |
| LLM | `GOOGLE_API_KEY` | Google API 키 | - |
| 데이터베이스 | `MARIADB_HOST` | MariaDB 호스트 | `localhost` |
| 데이터베이스 | `MARIADB_DATABASE` | 데이터베이스명 | `investment_analyst` |
| API 서버 | `API_HOST` | 서버 호스트 | `0.0.0.0` |
| API 서버 | `API_PORT` | 서버 포트 | `2400` |
| Redis | `REDIS_SENTINEL_HOSTS` | Redis Sentinel 호스트 | `localhost:26379` |
| OpenSearch | `OPENSEARCH_HOSTS` | OpenSearch 호스트 | `localhost:9200` |
| 로깅 | `LOG_LEVEL` | 로그 레벨 | `INFO` |

## 🧪 테스트

```bash
# 헬스체크 테스트
curl http://localhost:2400/api/v1/health

# 초기 데이터 수집 테스트
curl -X POST http://localhost:2400/api/v1/data/collect

# 전체 API 테스트 실행
python test_api.py
```

## 🐛 문제 해결

### 1. LLM 제공자 설정 오류
```bash
# 사용하려는 LLM 제공자의 패키지 설치
pip install openai  # OpenAI 사용 시
pip install google-generativeai  # Google Gemini 사용 시
pip install ollama  # Ollama 사용 시

# .env 파일에서 LLM_PROVIDER와 해당 API 키 설정 확인
```

### 2. 데이터베이스 초기화 오류
```bash
# SQLite 사용 시 데이터베이스 파일 삭제 후 재초기화
rm *.db
python init_app.py

# MariaDB 사용 시 연결 정보 확인
# MARIADB_HOST, MARIADB_USER, MARIADB_PASSWORD 등
```

### 3. 포트 충돌 오류
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :2400  # 백엔드 포트
lsof -i :2300  # 프론트엔드 포트

# 또는 다른 포트 사용
python run_server.py --port 2401
```

### 4. 벡터 모델 다운로드 오류
- 인터넷 연결 확인
- 또는 더 가벼운 모델로 변경

## 📝 개발 가이드

### 1. 새로운 API 엔드포인트 추가
`src/api/routes.py`에 새로운 라우터 함수를 추가합니다.

### 2. 새로운 서비스 추가
`src/services/` 디렉토리에 새로운 서비스 모듈을 생성합니다.

### 3. 새로운 LLM 제공자 추가
`src/services/llm_service.py`에 새로운 제공자 지원을 추가합니다.

### 4. 데이터베이스 모델 변경
`src/database/models.py`에서 모델을 수정하고 초기화 스크립트를 다시 실행합니다.

## 📄 라이선스

MIT License

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues를 통해 문의해주세요.