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
