import hashlib
import itertools
import math
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings


class EmbeddingError(RuntimeError):
    pass


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
        self.base_url = base_url.rstrip("/")
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
        payload = {"model": self.model, "input": texts}
        url = f"{self.base_url}/embeddings"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingError(f"Embedding provider request failed: {exc}") from exc

        data = response.json().get("data", [])
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


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.EMBEDDING_PROVIDER.lower().strip()
    if provider == "mock":
        return MockEmbeddingProvider(dim=settings.EMBEDDING_DIM)
    if provider in {"openai", "openai-compatible", "compatible"}:
        base_url = settings.EMBEDDING_BASE_URL or "https://api.openai.com/v1"
        return OpenAICompatibleEmbeddingProvider(
            base_url=base_url,
            api_key=settings.EMBEDDING_API_KEY,
            model=settings.EMBEDDING_MODEL,
            dim=settings.EMBEDDING_DIM,
            timeout_seconds=settings.EMBEDDING_TIMEOUT_SECONDS,
        )
    raise EmbeddingError(f"Unsupported EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")
