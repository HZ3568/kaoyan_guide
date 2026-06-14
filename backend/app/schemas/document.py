from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: int
    title: str
    file_name: str
    file_type: str
    source_type: str
    subject: str | None = None
    school: str | None = None
    major: str | None = None
    exam_year: int | None = None
    parse_status: str

    model_config = {"from_attributes": True}


class ChunkRead(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    token_count: int
    metadata_json: dict | None = None
    embedding_status: str

    model_config = {"from_attributes": True}
