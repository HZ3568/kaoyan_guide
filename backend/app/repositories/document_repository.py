from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def list_documents(
        self,
        user_id: int,
        *,
        knowledge_base_id: int | None = None,
        goal_id: int | None = None,
        domain: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        query = self.db.query(Document).filter(Document.user_id == user_id)
        if knowledge_base_id is not None:
            query = query.filter(Document.knowledge_base_id == knowledge_base_id)
        if goal_id is not None:
            query = query.filter(Document.goal_id == goal_id)
        if domain:
            query = query.filter(Document.domain == domain)
        if category:
            query = query.filter(Document.category == category)
        return query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    def get_document(self, document_id: int, user_id: int | None = None) -> Document | None:
        query = self.db.query(Document).filter(Document.id == document_id)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)
        return query.first()

    def add_chunks(self, chunks: list[DocumentChunk], *, commit: bool = True) -> None:
        self.db.add_all(chunks)
        if commit:
            self.db.commit()

    def list_chunks(self, document_id: int, user_id: int) -> list[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id, DocumentChunk.user_id == user_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )
