import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings


class LLMError(RuntimeError):
    pass


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    raw: dict[str, Any] | None = None


class LLMClient(ABC):
    provider: str
    model: str

    @abstractmethod
    def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        raise NotImplementedError


class MockLLMClient(LLMClient):
    provider = "mock"

    def __init__(self, model: str = "mock-learning") -> None:
        self.model = model

    def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        user_content = next((message.content for message in reversed(messages) if message.role == "user"), "")
        question = self._extract_section(user_content, "用户问题") or "用户问题"
        context = self._extract_section(user_content, "检索上下文") or ""
        context_lines = [
            line.strip()
            for line in context.splitlines()
            if line.strip() and not line.strip().startswith("[来源")
        ]
        evidence = "；".join(context_lines[:3])[:500]
        if evidence:
            answer = (
                f"根据当前知识库检索到的资料，针对“{question}”，可以依据以下信息回答："
                f"{evidence}\n\n请以前端展示的来源列表为准核对细节。"
            )
        else:
            answer = "当前知识库没有找到可靠依据，无法基于资料回答该问题。"
        return LLMResponse(content=answer, provider=self.provider, model=self.model)

    @staticmethod
    def _extract_section(text: str, title: str) -> str:
        pattern = rf"{re.escape(title)}：\n(.*?)(?:\n\n\S+：\n|\Z)"
        match = re.search(pattern, text, flags=re.S)
        return match.group(1).strip() if match else ""


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(
        self,
        *,
        provider: str,
        base_url: str,
        api_key: str | None,
        model: str,
        timeout_seconds: int,
    ) -> None:
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": settings.LLM_TEMPERATURE if temperature is None else temperature,
            "max_tokens": settings.LLM_MAX_TOKENS if max_tokens is None else max_tokens,
            "stream": False,
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM provider request failed: {exc}") from exc

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise LLMError("LLM provider returned no choices")
        content = choices[0].get("message", {}).get("content")
        if not content:
            raise LLMError("LLM provider returned empty content")
        return LLMResponse(content=content, provider=self.provider, model=self.model, raw=data)


def get_llm_client() -> LLMClient:
    provider = settings.LLM_PROVIDER.lower().strip()
    if provider == "mock":
        return MockLLMClient(model=settings.LLM_MODEL)
    if provider in {"openai", "openai-compatible", "compatible", "local"}:
        base_url = settings.LLM_BASE_URL or "https://api.openai.com/v1"
        return OpenAICompatibleLLMClient(
            provider=provider,
            base_url=base_url,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
        )
    raise LLMError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")
