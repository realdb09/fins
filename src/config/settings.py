"""
환경변수 기반 설정 관리
모든 설정은 .env 파일에서 로드하며 하드코딩을 금지합니다.
"""
import os
import logging
from typing import Optional, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class LLMSettings(BaseSettings):
    """LLM 관련 설정"""
    provider: str = Field(default="openai", env="LLM_PROVIDER")
    
    # Google/Gemini 설정
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-pro", env="GEMINI_MODEL")
    
    # OpenAI 설정
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    
    # Ollama 설정
    ollama_base_url: Optional[str] = Field(default=None, env="OLLAMA_BASE_URL")
    ollama_api_key: Optional[str] = Field(default=None, env="OLLAMA_API_KEY")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")
    
    # DeepInfra 설정
    deepinfra_api_key: Optional[str] = Field(default=None, env="DEEPINFRA_API_KEY")
    deepinfra_model: str = Field(default="meta-llama/Llama-2-70b-chat-hf", env="DEEPINFRA_MODEL")
    deepinfra_base_url: Optional[str] = Field(default=None, env="DEEPINFRA_BASE_URL")
    
    # 공통 LLM 설정
    temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=1000, env="LLM_MAX_TOKENS")
    timeout: int = Field(default=30, env="LLM_TIMEOUT")
    max_retries: int = Field(default=3, env="LLM_MAX_RETRIES")
    
    class Config:
        env_file = ".env"

class RedisSettings(BaseSettings):
    """Redis 설정"""
    sentinel_hosts: str = Field(default="localhost:26379", env="REDIS_SENTINEL_HOSTS")
    sentinel_service_name: str = Field(default="mymaster", env="REDIS_SENTINEL_SERVICE_NAME")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    socket_timeout: int = Field(default=30, env="REDIS_SOCKET_TIMEOUT")
    socket_connect_timeout: int = Field(default=30, env="REDIS_SOCKET_CONNECT_TIMEOUT")
    max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    
    class Config:
        env_file = ".env"

class OpenSearchSettings(BaseSettings):
    """OpenSearch 설정"""
    hosts: str = Field(default="localhost:9200", env="OPENSEARCH_HOSTS")
    user: str = Field(default="admin", env="OPENSEARCH_USER")
    password: str = Field(default="admin", env="OPENSEARCH_PASSWORD")
    use_ssl: bool = Field(default=False, env="OPENSEARCH_USE_SSL")
    verify_certs: bool = Field(default=False, env="OPENSEARCH_VERIFY_CERTS")
    ssl_assert_hostname: bool = Field(default=False, env="OPENSEARCH_SSL_ASSERT_HOSTNAME")
    ssl_show_warn: bool = Field(default=False, env="OPENSEARCH_SSL_SHOW_WARN")
    timeout: int = Field(default=30, env="OPENSEARCH_TIMEOUT")
    max_retries: int = Field(default=3, env="OPENSEARCH_MAX_RETRIES")
    retry_on_timeout: bool = Field(default=True, env="OPENSEARCH_RETRY_ON_TIMEOUT")
    
    class Config:
        env_file = ".env"

class MariaDBSettings(BaseSettings):
    """MariaDB 설정"""
    host: str = Field(default="localhost", env="MARIADB_HOST")
    port: int = Field(default=3306, env="MARIADB_PORT")
    user: str = Field(default="root", env="MARIADB_USER")
    password: str = Field(default="", env="MARIADB_PASSWORD")
    database: str = Field(default="investment_analyst", env="MARIADB_DATABASE")
    charset: str = Field(default="utf8mb4", env="MARIADB_CHARSET")
    connect_timeout: int = Field(default=10, env="MARIADB_CONNECT_TIMEOUT")
    read_timeout: int = Field(default=30, env="MARIADB_READ_TIMEOUT")
    write_timeout: int = Field(default=30, env="MARIADB_WRITE_TIMEOUT")
    
    class Config:
        env_file = ".env"

class AutogenSettings(BaseSettings):
    """Autogen 설정"""
    enabled: bool = Field(default=True, env="AUTOGEN_ENABLED")
    finance_group: str = Field(default="finance_analysts", env="AUTOGEN_FINANCE_GROUP")
    travel_group: str = Field(default="travel_experts", env="AUTOGEN_TRAVEL_GROUP")
    banking_group: str = Field(default="banking_specialists", env="AUTOGEN_BANKING_GROUP")
    max_round: int = Field(default=10, env="AUTOGEN_MAX_ROUND")
    timeout: int = Field(default=300, env="AUTOGEN_TIMEOUT")
    code_execution: bool = Field(default=False, env="AUTOGEN_CODE_EXECUTION")
    human_feedback: bool = Field(default=False, env="AUTOGEN_HUMAN_FEEDBACK")
    parallel: bool = Field(default=True, env="AUTOGEN_PARALLEL")
    cache: bool = Field(default=True, env="AUTOGEN_CACHE")
    
    class Config:
        env_file = ".env"

class LangfuseSettings(BaseSettings):
    """Langfuse 설정"""
    enabled: bool = Field(default=False, env="LANGFUSE_ENABLED")
    host: Optional[str] = Field(default=None, env="LANGFUSE_HOST")
    public_key: Optional[str] = Field(default=None, env="LANGFUSE_PUBLIC_KEY")
    secret_key: Optional[str] = Field(default=None, env="LANGFUSE_SECRET_KEY")
    debug: bool = Field(default=False, env="LANGFUSE_DEBUG")
    trace_llm: bool = Field(default=True, env="LANGFUSE_TRACE_LLM")
    trace_agents: bool = Field(default=True, env="LANGFUSE_TRACE_AGENTS")
    trace_autogen: bool = Field(default=True, env="LANGFUSE_TRACE_AUTOGEN")
    flush_at: int = Field(default=15, env="LANGFUSE_FLUSH_AT")
    flush_interval: int = Field(default=0.5, env="LANGFUSE_FLUSH_INTERVAL")
    timeout: int = Field(default=20, env="LANGFUSE_TIMEOUT")
    
    class Config:
        env_file = ".env"

class PhoenixSettings(BaseSettings):
    """Phoenix 설정"""
    enabled: bool = Field(default=False, env="PHOENIX_ENABLED")
    endpoint: Optional[str] = Field(default=None, env="PHOENIX_ENDPOINT")
    grpc_endpoint: Optional[str] = Field(default=None, env="PHOENIX_GRPC_ENDPOINT")
    trace_llm: bool = Field(default=True, env="PHOENIX_TRACE_LLM")
    trace_embeddings: bool = Field(default=True, env="PHOENIX_TRACE_EMBEDDINGS")
    trace_retrievals: bool = Field(default=True, env="PHOENIX_TRACE_RETRIEVALS")
    collect_metrics: bool = Field(default=True, env="PHOENIX_COLLECT_METRICS")
    sample_rate: float = Field(default=1.0, env="PHOENIX_SAMPLE_RATE")
    
    class Config:
        env_file = ".env"

class ExternalAPISettings(BaseSettings):
    """외부 API 설정"""
    # 검색 API
    google_search_api_key: Optional[str] = Field(default=None, env="GOOGLE_SEARCH_API_KEY")
    google_search_engine_id: Optional[str] = Field(default=None, env="GOOGLE_SEARCH_ENGINE_ID")
    naver_client_id: Optional[str] = Field(default=None, env="NAVER_CLIENT_ID")
    naver_client_secret: Optional[str] = Field(default=None, env="NAVER_CLIENT_SECRET")
    daum_app_key: Optional[str] = Field(default=None, env="DAUM_APP_KEY")
    
    # 금융 API
    bok_api_key: Optional[str] = Field(default=None, env="BOK_API_KEY")
    fss_api_key: Optional[str] = Field(default=None, env="FSS_API_KEY")
    koreaexim_api_key: Optional[str] = Field(default=None, env="KOREAEXIM_API_KEY")
    kftc_api_key: Optional[str] = Field(default=None, env="KFTC_API_KEY")
    kftc_client_id: Optional[str] = Field(default=None, env="KFTC_CLIENT_ID")
    kftc_client_secret: Optional[str] = Field(default=None, env="KFTC_CLIENT_SECRET")
    
    # 부동산 API
    molit_api_key: Optional[str] = Field(default=None, env="MOLIT_API_KEY")
    korea_land_api_key: Optional[str] = Field(default=None, env="KOREA_LAND_API_KEY")
    kb_real_estate_api_key: Optional[str] = Field(default=None, env="KB_REAL_ESTATE_API_KEY")
    
    class Config:
        env_file = ".env"

class APISettings(BaseSettings):
    """API 서버 설정"""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=2400, env="API_PORT")  # 백엔드 포트 2400으로 변경
    reload: bool = Field(default=True, env="API_RELOAD")
    log_level: str = Field(default="info", env="API_LOG_LEVEL")
    
    class Config:
        env_file = ".env"

class DatabaseSettings(BaseSettings):
    """데이터베이스 설정"""
    connection_pool_size: int = Field(default=10, env="DB_CONNECTION_POOL_SIZE")
    initialized: bool = Field(default=False, env="DB_INITIALIZED")
    testing_url: Optional[str] = Field(default=None, env="TESTING_DATABASE_URL")
    
    class Config:
        env_file = ".env"

class CacheSettings(BaseSettings):
    """캐시 설정"""
    ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    hit_threshold: float = Field(default=0.8, env="CACHE_HIT_THRESHOLD")
    eviction_policy: str = Field(default="lru", env="CACHE_EVICTION_POLICY")
    preload_enabled: bool = Field(default=True, env="PRELOAD_CACHE_ENABLED")
    
    class Config:
        env_file = ".env"

class Settings(BaseSettings):
    """전체 설정을 통합하는 메인 설정 클래스"""
    
    # 서브 설정 그룹
    llm: LLMSettings = LLMSettings()
    redis: RedisSettings = RedisSettings()
    opensearch: OpenSearchSettings = OpenSearchSettings()
    mariadb: MariaDBSettings = MariaDBSettings()
    autogen: AutogenSettings = AutogenSettings()
    langfuse: LangfuseSettings = LangfuseSettings()
    phoenix: PhoenixSettings = PhoenixSettings()
    external_api: ExternalAPISettings = ExternalAPISettings()
    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    cache: CacheSettings = CacheSettings()
    
    # 기본 설정
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    query_timeout_seconds: int = Field(default=30, env="QUERY_TIMEOUT_SECONDS")
    
    # 보안 설정
    secret_key: str = Field(default="default-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def setup_logging(self):
        """로깅 설정을 초기화합니다."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=log_format
        )
        
        # 민감한 정보 마스킹을 위한 커스텀 포매터
        if self.log_level.upper() in ["INFO", "WARNING", "ERROR"]:
            self._mask_sensitive_logs()
    
    def _mask_sensitive_logs(self):
        """민감한 정보를 로그에서 마스킹합니다."""
        sensitive_fields = [
            "api_key", "secret", "password", "token", "credential"
        ]
        # 실제 구현에서는 로그 포매터를 커스터마이징하여 민감한 필드를 마스킹
        pass

    def get_llm_config(self) -> dict:
        """현재 LLM 제공자에 따른 설정을 반환합니다."""
        provider = self.llm.provider.lower()
        
        if provider == "openai":
            return {
                "provider": "openai",
                "api_key": self.llm.openai_api_key,
                "model": self.llm.openai_model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries
            }
        elif provider == "google" or provider == "gemini":
            return {
                "provider": "google",
                "api_key": self.llm.google_api_key,
                "model": self.llm.gemini_model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries
            }
        elif provider == "ollama":
            return {
                "provider": "ollama",
                "base_url": self.llm.ollama_base_url,
                "api_key": self.llm.ollama_api_key,
                "model": self.llm.ollama_model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries
            }
        elif provider == "deepinfra":
            return {
                "provider": "deepinfra",
                "api_key": self.llm.deepinfra_api_key,
                "base_url": self.llm.deepinfra_base_url,
                "model": self.llm.deepinfra_model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries
            }
        else:
            raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")

# 싱글톤 설정 인스턴스
settings = Settings()