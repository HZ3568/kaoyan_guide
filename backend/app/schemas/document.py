from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: int
    title: str
    file_name: str
    file_type: str
    source: str | None = None
    source_type: str
    source_url: str | None = None
    subject: str | None = None
    school: str | None = None
    major: str | None = None
    tags_json: list | None = None
    exam_year: int | None = None
    parse_status: str

    model_config = {"from_attributes": True}


class ChunkRead(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    chunk_type: str
    page_number: int | None = None
    position_start: int | None = None
    position_end: int | None = None
    token_count: int
    metadata_json: dict | None = None
    embedding_status: str
    is_vectorized: bool

    model_config = {"from_attributes": True}


class LocalImportRequest(BaseModel):
    path: str
    recursive: bool = True
    title: str | None = None
    source: str | None = None
    source_url: str | None = None
    subject: str | None = None
    school: str | None = None
    major: str | None = None
    tags: list[str] | None = None
    exam_year: int | None = None
    description: str | None = None


class LocalImportError(BaseModel):
    path: str
    error: str


class LocalImportResponse(BaseModel):
    imported: list[DocumentRead]
    errors: list[LocalImportError] = []
