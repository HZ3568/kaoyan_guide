from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.chunk import DocumentChunk
from app.repositories.document_repository import DocumentRepository
from app.services.ingestion_service import IngestionService, UnsupportedDocumentTypeError


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.repo = DocumentRepository(db)
        self.ingestion = IngestionService()

    async def upload_and_parse(self, file: UploadFile, user_id: int | None = None):
        raw_dir = Path(settings.RAW_DATA_DIR)
        raw_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "upload.txt").suffix.lower()
        saved_name = f"{uuid4().hex}{suffix}"
        saved_path = raw_dir / saved_name
        content = await file.read()
        saved_path.write_bytes(content)

        doc = self.repo.create_document(
            user_id=user_id,
            title=Path(file.filename or saved_name).stem,
            file_name=file.filename or saved_name,
            file_type=suffix.lstrip(".") or "unknown",
            file_path=str(saved_path),
            parse_status="parsing",
        )

        try:
            text = self.ingestion.parse_file(str(saved_path))
            chunks_text = self.ingestion.split_chunks(text)
        except UnsupportedDocumentTypeError:
            doc.parse_status = "unsupported"
            self.repo.db.commit()
            self.repo.db.refresh(doc)
            return doc
        except Exception:
            doc.parse_status = "failed"
            self.repo.db.commit()
            self.repo.db.refresh(doc)
            return doc

        if not chunks_text:
            doc.parse_status = "empty"
            self.repo.db.commit()
            self.repo.db.refresh(doc)
            return doc

        chunks = [
            DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                content=chunk,
                content_hash=self.ingestion.content_hash(chunk),
                token_count=len(chunk),
                metadata_json={"file_name": doc.file_name, "title": doc.title},
            )
            for i, chunk in enumerate(chunks_text)
        ]
        self.repo.add_chunks(chunks)
        doc.parse_status = "parsed"
        self.repo.db.commit()
        self.repo.db.refresh(doc)
        return doc

    def list_documents(self, user_id: int):
        return self.repo.list_documents(user_id=user_id)

    def get_document(self, document_id: int, user_id: int):
        doc = self.repo.get_document(document_id, user_id=user_id)
        if not doc:
            raise NotFoundError("Document not found")
        return doc

    def list_chunks(self, document_id: int, user_id: int):
        self.get_document(document_id, user_id=user_id)
        return self.repo.list_chunks(document_id, user_id=user_id)
