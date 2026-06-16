from typing import Any

from pydantic import AliasChoices, BaseModel, Field


class RetrievalFilter(BaseModel):
    goal_id: int | None = None
    knowledge_base_id: int | None = None
    domain: str | None = None
    category: str | None = None


class VectorIndexRequest(BaseModel):
    document_id: int | None = None
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    limit: int = Field(default=100, ge=1, le=1000)
    batch_size: int = Field(default=32, ge=1, le=128)
    force_reindex: bool = False


class VectorIndexResponse(BaseModel):
    indexed: int
    skipped: int
    failed: int
    errors: list[str] = Field(default_factory=list)
    index_name: str
    embedding_dim: int
    dimension_notice: str | None = None


class RagSearchRequest(BaseModel):
    question: str = Field(validation_alias=AliasChoices("question", "query"), min_length=1)
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    filters: RetrievalFilter | None = None

    model_config = {"populate_by_name": True}


class RagSource(BaseModel):
    chunk_id: int
    document_id: int
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    score: float
    filename: str | None = None
    original_filename: str | None = None
    domain: str | None = None
    category: str | None = None
    content_preview: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagSearchResult(RagSource):
    content: str


class RagAskRequest(BaseModel):
    question: str = Field(min_length=1)
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    filters: RetrievalFilter | None = None
    stream: bool = False


class RagAskResponse(BaseModel):
    answer: str
    sources: list[RagSource] = Field(default_factory=list)
    hit_source: bool = False
    model_provider: str | None = None
    model_name: str | None = None
    log_id: int | None = None
    retrieval_debug: dict[str, Any] = Field(default_factory=dict)


class VectorIndexStatus(BaseModel):
    total_chunks: int
    indexed_chunks: int
    pending_chunks: int
    failed_chunks: int
    redis: dict[str, Any] = Field(default_factory=dict)
    embedding: dict[str, Any] = Field(default_factory=dict)
    dimension_notice: str | None = None


class EmbeddingConnectivityResponse(BaseModel):
    ok: bool
    provider: str
    base_url: str | None = None
    model: str
    dimension: int
    status_code: int | None = None
    message: str
    error_body: str | None = None
    hints: list[str] = Field(default_factory=list)
    dimension_notice: str | None = None
