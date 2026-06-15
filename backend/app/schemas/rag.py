from pydantic import BaseModel, Field


class RetrievalFilter(BaseModel):
    subject: str | None = None
    school: str | None = None
    major: str | None = None
    year: int | None = None


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    filters: RetrievalFilter | None = None


class VectorIndexRequest(BaseModel):
    document_id: int | None = None
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


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    filters: RetrievalFilter | None = None


class RagSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    score: float
    content: str
    source: dict = Field(default_factory=dict)
    page_number: int | None = None
    location: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class VectorIndexStatus(BaseModel):
    total_chunks: int
    indexed_chunks: int
    pending_chunks: int
    failed_chunks: int
    redis: dict = Field(default_factory=dict)


class RagAskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    filters: RetrievalFilter | None = None
    session_id: int | None = None
    stream: bool = False


class RagSource(BaseModel):
    chunk_id: int
    document_id: int
    score: float
    title: str | None = None
    source: str | None = None
    source_type: str | None = None
    source_url: str | None = None
    file_name: str | None = None
    page_number: int | None = None
    location: dict = Field(default_factory=dict)
    content_preview: str
    metadata: dict = Field(default_factory=dict)


class RagAskResponse(BaseModel):
    answer: str
    sources: list[RagSource] = Field(default_factory=list)
    hit_source: bool = False
    model_provider: str | None = None
    model_name: str | None = None
    log_id: int | None = None
    retrieval_debug: dict = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk_id: int
    document_id: int | None = None
    content: str
    score: float
    metadata: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    question: str
    session_id: int | None = None
    filters: RetrievalFilter | None = None


class Citation(BaseModel):
    document_id: int | None = None
    chunk_id: int
    document_title: str | None = None
    content_preview: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    retrieval_debug: dict = Field(default_factory=dict)
