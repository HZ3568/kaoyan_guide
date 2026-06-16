import hashlib
import itertools
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

DIMENSION_REBUILD_NOTICE = (
    "如果 EMBEDDING_DIMENSION 从旧值变更，需要删除旧 Redis Vector Index，"
    "并重新向量化文档，否则旧索引维度可能与新 embedding 不一致。"
)


class EmbeddingError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_body = error_body


@dataclass
class EmbeddingConnectivityResult:
    ok: bool
    provider: str
    base_url: str | None
    model: str
    dimension: int
    status_code: int | None = None
    message: str = ""
    error_body: str | None = None
    hints: list[str] | None = None
    dimension_notice: str = DIMENSION_REBUILD_NOTICE


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dim(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    """开发占位 embedding：可跑通流程，不代表真实语义效果。"""

    def __init__(self, dim: int = 128) -> None:
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def _embed(self, text: str) -> list[float]:
        seed = text.encode("utf-8")
        digest_stream = itertools.chain.from_iterable(
            hashlib.sha256(seed + i.to_bytes(4, "little")).digest()
            for i in range(math.ceil(self.dim / 32))
        )
        values = [(next(digest_stream) / 255.0) for _ in range(self.dim)]
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]


class OpenAICompatibleEmbeddingProvider(EmbeddingProvider):
    """OpenAI compatible /v1/embeddings provider."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        model: str,
        dim: int,
        timeout_seconds: int,
    ) -> None:
        self.base_url = self._normalize_base_url(base_url)
        self.api_key = api_key
        self.model = model
        self._dim = dim
        self.timeout_seconds = timeout_seconds

    @property
    def dim(self) -> int:
        return self._dim

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": self.model, "input": texts, "dimensions": self.dim}
        url = f"{self.base_url}/embeddings"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise self._build_status_error(exc.response) from exc
        except httpx.RequestError as exc:
            message = (
                "Embedding provider network request failed: "
                f"base_url={self.base_url}, model={self.model}, dimension={self.dim}, error={exc}"
            )
            logger.error(message)
            raise EmbeddingError(message) from exc

        try:
            data = response.json().get("data", [])
        except ValueError as exc:
            message = (
                "Embedding provider returned invalid JSON: "
                f"base_url={self.base_url}, model={self.model}, dimension={self.dim}, "
                f"status_code={response.status_code}, body={self._response_text(response)}"
            )
            logger.error(message)
            raise EmbeddingError(message, status_code=response.status_code) from exc
        ordered = sorted(data, key=lambda item: item.get("index", 0))
        embeddings = [item.get("embedding", []) for item in ordered]
        if len(embeddings) != len(texts):
            raise EmbeddingError(
                f"Embedding provider returned {len(embeddings)} vectors for {len(texts)} inputs"
            )
        for embedding in embeddings:
            if len(embedding) != self.dim:
                raise EmbeddingError(
                    f"Embedding dimension mismatch: expected {self.dim}, got {len(embedding)}"
                )
        return embeddings

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        normalized = base_url.rstrip("/")
        if normalized.endswith("/embeddings"):
            normalized = normalized[: -len("/embeddings")]
        return normalized

    def _build_status_error(self, response: httpx.Response) -> EmbeddingError:
        error_body = self._response_text(response)
        hints = embedding_error_hints(response.status_code)
        message = (
            "Embedding provider request failed: "
            f"base_url={self.base_url}, model={self.model}, dimension={self.dim}, "
            f"status_code={response.status_code}, error_body={error_body}"
        )
        if hints:
            message = f"{message}; hints={'；'.join(hints)}"
        logger.error(
            "Embedding provider request failed base_url=%s model=%s dimension=%s status_code=%s error_body=%s",
            self.base_url,
            self.model,
            self.dim,
            response.status_code,
            error_body,
        )
        return EmbeddingError(
            message,
            status_code=response.status_code,
            error_body=error_body,
        )

    @staticmethod
    def _response_text(response: httpx.Response) -> str:
        text = response.text.strip()
        if len(text) > 1000:
            return f"{text[:1000]}..."
        return text


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.EMBEDDING_PROVIDER.lower().strip()
    if provider == "mock":
        return MockEmbeddingProvider(dim=settings.embedding_dimension)
    if provider in {"openai", "openai-compatible", "compatible"}:
        base_url = settings.EMBEDDING_BASE_URL or _default_embedding_base_url(provider)
        return OpenAICompatibleEmbeddingProvider(
            base_url=base_url,
            api_key=settings.EMBEDDING_API_KEY,
            model=settings.EMBEDDING_MODEL,
            dim=settings.embedding_dimension,
            timeout_seconds=settings.EMBEDDING_TIMEOUT_SECONDS,
        )
    raise EmbeddingError(f"Unsupported EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")


def check_embedding_connectivity() -> EmbeddingConnectivityResult:
    provider = get_embedding_provider()
    provider_name = settings.EMBEDDING_PROVIDER.lower().strip()
    base_url = getattr(provider, "base_url", settings.EMBEDDING_BASE_URL)
    model = getattr(provider, "model", settings.EMBEDDING_MODEL)
    try:
        embedding = provider.embed_query("embedding connectivity check")
    except EmbeddingError as exc:
        return EmbeddingConnectivityResult(
            ok=False,
            provider=provider_name,
            base_url=base_url,
            model=model,
            dimension=provider.dim,
            status_code=exc.status_code,
            message=str(exc),
            error_body=exc.error_body,
            hints=embedding_error_hints(exc.status_code),
        )

    return EmbeddingConnectivityResult(
        ok=len(embedding) == provider.dim,
        provider=provider_name,
        base_url=base_url,
        model=model,
        dimension=provider.dim,
        message="Embedding provider is reachable.",
        hints=[],
    )


def embedding_runtime_config() -> dict[str, Any]:
    provider = settings.EMBEDDING_PROVIDER.lower().strip()
    return {
        "provider": provider,
        "base_url": settings.EMBEDDING_BASE_URL or _default_embedding_base_url(provider),
        "model": settings.EMBEDDING_MODEL,
        "dimension": settings.embedding_dimension,
        "dimension_notice": DIMENSION_REBUILD_NOTICE,
    }


def embedding_error_hints(status_code: int | None) -> list[str]:
    if status_code == 403:
        return [
            "API Key 无权限",
            "模型未开通",
            "分组权限不足",
            "余额或白名单限制",
        ]
    if status_code == 401:
        return ["API Key 无效或未配置"]
    if status_code == 404:
        return ["Embedding base_url 或模型名称不正确"]
    if status_code == 429:
        return ["请求频率或额度受限"]
    return []


def _default_embedding_base_url(provider: str) -> str:
    if provider == "openai":
        return "https://api.openai.com/v1"
    return "https://api.v3.cm/v1"
