from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BadRequestError
from app.ingestion.chunkers import chunk_loaded_document, normalize_table_fields
from app.ingestion.loaders import (
    DocumentLoadError,
    LoadedDocument,
    LoadedTableRow,
    SUPPORTED_EXTENSIONS,
    UnsupportedDocumentTypeError,
    load_document,
)
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.ocr import OcrTableRecord, OcrTask
from app.rag.chunk_schema import SourceInfo
from app.repositories.document_repository import DocumentRepository


@dataclass(frozen=True)
class DocumentImportOptions:
    user_id: int | None = None
    title: str | None = None
    source: str | None = None
    source_type: str = "uploaded"
    source_url: str | None = None
    subject: str | None = None
    school: str | None = None
    major: str | None = None
    tags: list[str] | None = None
    exam_year: int | None = None
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
        file_name = options.original_file_name or path.name
        suffix = path.suffix.lower()
        doc = self.repo.create_document(
            user_id=options.user_id,
            title=options.title or Path(file_name).stem,
            file_name=file_name,
            file_type=suffix.lstrip(".") or "unknown",
            file_path=str(path),
            source=options.source,
            source_type=options.source_type,
            source_url=options.source_url,
            subject=options.subject,
            school=options.school,
            major=options.major,
            tags_json=options.tags,
            exam_year=options.exam_year,
            description=options.description,
            parse_status="parsing",
        )

        try:
            loaded = load_document(path)
            source_info = SourceInfo(
                file_name=file_name,
                file_path=str(path),
                source=options.source,
                source_type=options.source_type,
                source_url=options.source_url,
            )
            chunks = chunk_loaded_document(loaded, source_info)
        except UnsupportedDocumentTypeError:
            doc.parse_status = "unsupported"
            self.db.commit()
            self.db.refresh(doc)
            return doc
        except DocumentLoadError:
            doc.parse_status = "failed"
            self.db.commit()
            self.db.refresh(doc)
            return doc
        except Exception:
            self.db.rollback()
            doc = self.repo.get_document(doc.id) or doc
            doc.parse_status = "failed"
            self.db.commit()
            self.db.refresh(doc)
            return doc

        if not chunks:
            doc.parse_status = "empty"
            self.db.commit()
            self.db.refresh(doc)
            return doc

        try:
            db_chunks = [
                DocumentChunk(
                    document_id=doc.id,
                    chunk_index=index,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type,
                    page_number=chunk.page_number,
                    position_start=chunk.position_start,
                    position_end=chunk.position_end,
                    content_hash=content_hash(chunk.content),
                    token_count=chunk.token_count,
                    metadata_json={
                        **chunk.metadata,
                        "document_id": doc.id,
                        "document_title": doc.title,
                        "file_type": doc.file_type,
                    },
                )
                for index, chunk in enumerate(chunks)
            ]
            self.repo.add_chunks(db_chunks, commit=False)

            if loaded.raw_json is not None:
                self._persist_ocr_records(doc, loaded, options)

            doc.parse_status = "parsed"
            self.db.commit()
        except Exception:
            self.db.rollback()
            doc = self.repo.get_document(doc.id) or doc
            doc.parse_status = "failed"
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
                    title=options.title if target.is_file() else None,
                    source=options.source,
                    source_type=options.source_type or "local",
                    source_url=options.source_url,
                    subject=options.subject,
                    school=options.school,
                    major=options.major,
                    tags=options.tags,
                    exam_year=options.exam_year,
                    description=options.description,
                )
                doc = self.import_file(file_path, file_options)
                result.imported.append(doc)
            except Exception as exc:
                self.db.rollback()
                result.errors.append({"path": str(file_path), "error": str(exc)})
        return result

    def _persist_ocr_records(
        self,
        doc: Document,
        loaded: LoadedDocument,
        options: DocumentImportOptions,
    ) -> None:
        ocr_task = OcrTask(
            user_id=options.user_id,
            document_id=doc.id,
            image_path=str(loaded.path),
            engine="json_import",
            raw_json=loaded.raw_json,
            status="parsed",
        )
        self.db.add(ocr_task)
        self.db.flush()

        for row in loaded.table_rows:
            self.db.add(_table_record_from_row(row, doc.id, ocr_task.id, str(loaded.path)))


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _table_record_from_row(
    row: LoadedTableRow,
    document_id: int,
    ocr_task_id: int,
    default_path: str,
) -> OcrTableRecord:
    fields = normalize_table_fields(row.values)
    return OcrTableRecord(
        ocr_task_id=ocr_task_id,
        document_id=document_id,
        source_image_path=row.source_image_path or default_path,
        source_page_number=row.page_number or _as_int(row.metadata.get("page_number")),
        school=_as_str(fields.get("school")),
        major=_as_str(fields.get("major")),
        research_direction=_as_str(fields.get("research_direction")),
        exam_subjects=_as_str(fields.get("exam_subjects")),
        score_line=_as_str(fields.get("score_line")),
        enrollment_count=_as_int(fields.get("enrollment_count")),
        note=_as_str(fields.get("note")),
        raw_row_json=row.values,
    )


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


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return None
    return int(digits)
