"""
LLM 서비스
다양한 LLM 제공자를 통합하여 관리하는 서비스입니다.
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.config.settings import settings

logger = logging.getLogger(__name__)

class LLMService:
    """LLM 통합 서비스"""
    
    def __init__(self):
        self.config = settings.get_llm_config()
        self.provider = self.config["provider"]
        self._initialize_client()
    
    def _initialize_client(self):
        """LLM 클라이언트를 초기화합니다."""
        try:
            if self.provider == "openai":
                self._initialize_openai()
            elif self.provider == "google":
                self._initialize_google()
            elif self.provider == "ollama":
                self._initialize_ollama()
            elif self.provider == "deepinfra":
                self._initialize_deepinfra()
            else:
                raise ValueError(f"지원하지 않는 LLM 제공자: {self.provider}")
            
            logger.info(f"LLM 클라이언트 초기화 완료: {self.provider}")
            
        except Exception as e:
            logger.error(f"LLM 클라이언트 초기화 실패: {e}")
            raise
    
    def _initialize_openai(self):
        """OpenAI 클라이언트 초기화"""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.config["api_key"],
                timeout=self.config["timeout"],
                max_retries=self.config["max_retries"]
            )
        except ImportError:
            logger.error("OpenAI 패키지가 설치되지 않았습니다: pip install openai")
            raise
    
    def _initialize_google(self):
        """Google Gemini 클라이언트 초기화"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config["api_key"])
            self.client = genai.GenerativeModel(self.config["model"])
        except ImportError:
            logger.error("Google AI 패키지가 설치되지 않았습니다: pip install google-generativeai")
            raise
    
    def _initialize_ollama(self):
        """Ollama 클라이언트 초기화"""
        try:
            import ollama
            self.client = ollama.Client(
                host=self.config["base_url"],
                timeout=self.config["timeout"]
            )
        except ImportError:
            logger.error("Ollama 패키지가 설치되지 않았습니다: pip install ollama")
            raise
    
    def _initialize_deepinfra(self):
        """DeepInfra 클라이언트 초기화"""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.config["api_key"],
                base_url=self.config["base_url"],
                timeout=self.config["timeout"],
                max_retries=self.config["max_retries"]
            )
        except ImportError:
            logger.error("OpenAI 패키지가 설치되지 않았습니다: pip install openai")
            raise
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """LLM을 사용하여 응답을 생성합니다."""
        try:
            if self.provider == "openai":
                return await self._generate_openai_response(prompt, system_prompt)
            elif self.provider == "google":
                return await self._generate_google_response(prompt, system_prompt)
            elif self.provider == "ollama":
                return await self._generate_ollama_response(prompt, system_prompt)
            elif self.provider == "deepinfra":
                return await self._generate_deepinfra_response(prompt, system_prompt)
            else:
                raise ValueError(f"지원하지 않는 LLM 제공자: {self.provider}")
        
        except Exception as e:
            logger.error(f"LLM 응답 생성 실패: {e}")
            return f"죄송합니다. 현재 AI 서비스에 문제가 발생했습니다: {str(e)}"
    
    async def _generate_openai_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """OpenAI API를 사용하여 응답 생성"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
        )
        
        return response.choices[0].message.content
    
    async def _generate_google_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Google Gemini API를 사용하여 응답 생성"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": self.config["temperature"],
                    "max_output_tokens": self.config["max_tokens"]
                }
            )
        )
        
        return response.text
    
    async def _generate_ollama_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Ollama API를 사용하여 응답 생성"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat(
                model=self.config["model"],
                messages=messages,
                options={
                    "temperature": self.config["temperature"],
                    "num_predict": self.config["max_tokens"]
                }
            )
        )
        
        return response["message"]["content"]
    
    async def _generate_deepinfra_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """DeepInfra API를 사용하여 응답 생성"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
        )
        
        return response.choices[0].message.content
    
    def get_provider_info(self) -> Dict[str, Any]:
        """현재 LLM 제공자 정보를 반환합니다."""
        return {
            "provider": self.provider,
            "model": self.config["model"],
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"],
            "timeout": self.config["timeout"],
            "max_retries": self.config["max_retries"]
        }

# 싱글톤 LLM 서비스
llm_service = LLMService()