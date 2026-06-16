from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.ingestion.pipeline import DocumentImportOptions, DocumentImportPipeline, LocalImportResult
from app.repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.repo = DocumentRepository(db)
        self.pipeline = DocumentImportPipeline(db)

    async def upload_and_parse(
        self,
        file: UploadFile,
        *,
        user_id: int,
        knowledge_base_id: int | None = None,
        goal_id: int | None = None,
        domain: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
    ):
        raw_dir = Path(settings.RAW_DATA_DIR)
        raw_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "upload.txt").suffix.lower()
        saved_name = f"{uuid4().hex}{suffix}"
        saved_path = raw_dir / saved_name
        content = await file.read()
        saved_path.write_bytes(content)

        return self.pipeline.import_file(
            saved_path,
            DocumentImportOptions(
                user_id=user_id,
                knowledge_base_id=knowledge_base_id,
                goal_id=goal_id,
                domain=domain,
                category=category,
                tags=tags,
                description=description,
                original_file_name=file.filename or saved_name,
            ),
        )

    def import_local(
        self,
        path: str,
        *,
        user_id: int,
        recursive: bool = True,
        knowledge_base_id: int | None = None,
        goal_id: int | None = None,
        domain: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
    ) -> LocalImportResult:
        return self.pipeline.import_local_path(
            path,
            DocumentImportOptions(
                user_id=user_id,
                knowledge_base_id=knowledge_base_id,
                goal_id=goal_id,
                domain=domain,
                category=category,
                tags=tags,
                description=description,
            ),
            recursive=recursive,
        )

    def list_documents(
        self,
        *,
        user_id: int,
        knowledge_base_id: int | None = None,
        goal_id: int | None = None,
        domain: str | None = None,
        category: str | None = None,
    ):
        return self.repo.list_documents(
            user_id=user_id,
            knowledge_base_id=knowledge_base_id,
            goal_id=goal_id,
            domain=domain,
            category=category,
        )

    def get_document(self, document_id: int, user_id: int):
        doc = self.repo.get_document(document_id, user_id=user_id)
        if not doc:
            raise NotFoundError("Document not found")
        return doc

    def list_chunks(self, document_id: int, user_id: int):
        self.get_document(document_id, user_id=user_id)
        return self.repo.list_chunks(document_id, user_id=user_id)
