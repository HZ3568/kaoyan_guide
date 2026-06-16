from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    domain: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=128)
    tags: list[str] | None = None
    description: str | None = None


class DocumentOut(BaseModel):
    id: int
    user_id: int
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    filename: str
    original_filename: str | None = None
    file_type: str
    file_path: str
    domain: str | None = None
    category: str | None = None
    tags_json: list[str] | None = None
    parse_status: str
    chunk_status: str
    embedding_status: str
    chunk_count: int
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentChunkOut(BaseModel):
    id: int
    document_id: int
    user_id: int
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    chunk_index: int
    content: str
    content_hash: str
    domain: str | None = None
    category: str | None = None
    metadata_json: dict[str, Any] | None = None
    embedding_id: str | None = None
    embedding_status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class LocalImportRequest(DocumentCreate):
    path: str
    recursive: bool = True


class LocalImportError(BaseModel):
    path: str
    error: str


class LocalImportResponse(BaseModel):
    imported: list[DocumentOut]
    errors: list[LocalImportError] = []
