from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BadRequestError
from app.ingestion.chunkers import chunk_loaded_document
from app.ingestion.loaders import (
    DocumentLoadError,
    SUPPORTED_EXTENSIONS,
    UnsupportedDocumentTypeError,
    load_document,
)
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.rag.chunk_schema import SourceInfo
from app.repositories.document_repository import DocumentRepository


@dataclass(frozen=True)
class DocumentImportOptions:
    user_id: int
    knowledge_base_id: int | None = None
    goal_id: int | None = None
    domain: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    description: str | None = None
    original_file_name: str | None = None


@dataclass
class LocalImportResult:
    imported: list[Document] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


class DocumentImportPipeline:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DocumentRepository(db)

    def import_file(self, file_path: str | Path, options: DocumentImportOptions) -> Document:
        path = Path(file_path)
        original_filename = options.original_file_name or path.name
        suffix = path.suffix.lower()
        doc = self.repo.create_document(
            user_id=options.user_id,
            knowledge_base_id=options.knowledge_base_id,
            goal_id=options.goal_id,
            filename=path.name,
            original_filename=original_filename,
            file_type=suffix.lstrip(".") or "unknown",
            file_path=str(path),
            domain=options.domain,
            category=options.category,
            tags_json=options.tags,
            description=options.description,
            parse_status="parsing",
            chunk_status="pending",
            embedding_status="pending",
            chunk_count=0,
        )

        try:
            loaded = load_document(path)
            source_info = SourceInfo(
                file_name=original_filename,
                file_path=str(path),
                source=options.category,
                source_type="uploaded",
                source_url=None,
            )
            chunks = chunk_loaded_document(loaded, source_info)
        except UnsupportedDocumentTypeError:
            doc.parse_status = "unsupported"
            doc.chunk_status = "skipped"
            self.db.commit()
            self.db.refresh(doc)
            return doc
        except DocumentLoadError:
            doc.parse_status = "failed"
            doc.chunk_status = "failed"
            self.db.commit()
            self.db.refresh(doc)
            return doc
        except Exception:
            self.db.rollback()
            doc = self.repo.get_document(doc.id) or doc
            doc.parse_status = "failed"
            doc.chunk_status = "failed"
            self.db.commit()
            self.db.refresh(doc)
            return doc

        if not chunks:
            doc.parse_status = "empty"
            doc.chunk_status = "empty"
            self.db.commit()
            self.db.refresh(doc)
            return doc

        try:
            db_chunks = [
                DocumentChunk(
                    document_id=doc.id,
                    user_id=doc.user_id,
                    knowledge_base_id=doc.knowledge_base_id,
                    goal_id=doc.goal_id,
                    chunk_index=index,
                    content=chunk.content,
                    content_hash=content_hash(chunk.content),
                    domain=doc.domain,
                    category=doc.category,
                    metadata_json={
                        **chunk.metadata,
                        "document_id": doc.id,
                        "filename": doc.filename,
                        "original_filename": doc.original_filename,
                        "file_type": doc.file_type,
                        "chunk_type": chunk.chunk_type,
                        "page_number": chunk.page_number,
                        "position_start": chunk.position_start,
                        "position_end": chunk.position_end,
                        "token_count": chunk.token_count,
                    },
                    embedding_status="pending",
                )
                for index, chunk in enumerate(chunks)
            ]
            self.repo.add_chunks(db_chunks, commit=False)
            doc.parse_status = "parsed"
            doc.chunk_status = "chunked"
            doc.chunk_count = len(db_chunks)
            self.db.commit()
        except Exception:
            self.db.rollback()
            doc = self.repo.get_document(doc.id) or doc
            doc.parse_status = "failed"
            doc.chunk_status = "failed"
            self.db.commit()
        finally:
            self.db.refresh(doc)
        return doc

    def import_local_path(
        self,
        requested_path: str,
        options: DocumentImportOptions,
        *,
        recursive: bool = True,
    ) -> LocalImportResult:
        if not settings.ALLOW_LOCAL_IMPORTS:
            raise BadRequestError("Local import is disabled")

        root = Path(settings.LOCAL_IMPORT_ROOT or settings.DATA_DIR).resolve()
        target = _resolve_import_path(requested_path, root)
        if not target.exists():
            raise BadRequestError(f"Import path does not exist: {requested_path}")

        files = _iter_supported_files(target, recursive=recursive)
        result = LocalImportResult()
        for file_path in files:
            try:
                file_options = DocumentImportOptions(
                    user_id=options.user_id,
                    knowledge_base_id=options.knowledge_base_id,
                    goal_id=options.goal_id,
                    domain=options.domain,
                    category=options.category,
                    tags=options.tags,
                    description=options.description,
                )
                doc = self.import_file(file_path, file_options)
                result.imported.append(doc)
            except Exception as exc:
                self.db.rollback()
                result.errors.append({"path": str(file_path), "error": str(exc)})
        return result


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _iter_supported_files(target: Path, *, recursive: bool) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix.lower() in SUPPORTED_EXTENSIONS else []
    iterator = target.rglob("*") if recursive else target.glob("*")
    return sorted(path for path in iterator if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS)


def _resolve_import_path(requested_path: str, root: Path) -> Path:
    target = Path(requested_path).expanduser()
    if not target.is_absolute():
        target = root / target
    resolved = target.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BadRequestError(f"Import path must be under local import root: {root}") from exc
    return resolved
