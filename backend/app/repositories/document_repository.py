from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chunk import DocumentChunk


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def list_documents(self, user_id: int, skip: int = 0, limit: int = 50) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_document(self, document_id: int, user_id: int | None = None) -> Document | None:
        query = self.db.query(Document).filter(Document.id == document_id)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)
        return query.first()

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        self.db.add_all(chunks)
        self.db.commit()

    def list_chunks(self, document_id: int, user_id: int) -> list[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(DocumentChunk.document_id == document_id)
            .filter(Document.user_id == user_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )
