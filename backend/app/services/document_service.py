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
        user_id: int | None = None,
        *,
        title: str | None = None,
        source: str | None = None,
        source_url: str | None = None,
        subject: str | None = None,
        school: str | None = None,
        major: str | None = None,
        tags: list[str] | None = None,
        exam_year: int | None = None,
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
                title=title,
                source=source,
                source_type="uploaded",
                source_url=source_url,
                subject=subject,
                school=school,
                major=major,
                tags=tags,
                exam_year=exam_year,
                description=description,
                original_file_name=file.filename or saved_name,
            ),
        )

    def import_local(
        self,
        path: str,
        user_id: int | None = None,
        *,
        recursive: bool = True,
        title: str | None = None,
        source: str | None = None,
        source_url: str | None = None,
        subject: str | None = None,
        school: str | None = None,
        major: str | None = None,
        tags: list[str] | None = None,
        exam_year: int | None = None,
        description: str | None = None,
    ) -> LocalImportResult:
        return self.pipeline.import_local_path(
            path,
            DocumentImportOptions(
                user_id=user_id,
                title=title,
                source=source,
                source_type="local",
                source_url=source_url,
                subject=subject,
                school=school,
                major=major,
                tags=tags,
                exam_year=exam_year,
                description=description,
            ),
            recursive=recursive,
        )

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
