from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class UnsupportedDocumentTypeError(ValueError):
    pass


class DocumentLoadError(RuntimeError):
    pass


@dataclass(frozen=True)
class LoadedTextBlock:
    text: str
    block_type: str = "text"
    page_number: int | None = None
    position_start: int | None = None
    position_end: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LoadedTableRow:
    values: dict[str, Any]
    page_number: int | None = None
    source_image_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LoadedDocument:
    path: Path
    file_type: str
    text_blocks: list[LoadedTextBlock] = field(default_factory=list)
    table_rows: list[LoadedTableRow] = field(default_factory=list)
    raw_json: Any | None = None


TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv"}
OCR_JSON_EXTENSIONS = {".json"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | OCR_JSON_EXTENSIONS | PDF_EXTENSIONS


def load_document(file_path: str | Path) -> LoadedDocument:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return _load_text(path, suffix)
    if suffix in PDF_EXTENSIONS:
        return _load_pdf(path)
    if suffix in OCR_JSON_EXTENSIONS:
        return _load_ocr_json(path)
    raise UnsupportedDocumentTypeError(f"Unsupported document type: {suffix or 'unknown'}")


def _load_text(path: Path, suffix: str) -> LoadedDocument:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return LoadedDocument(
        path=path,
        file_type=suffix.lstrip("."),
        text_blocks=[
            LoadedTextBlock(
                text=text,
                position_start=0,
                position_end=len(text),
                metadata={"loader": "text"},
            )
        ],
    )


def _load_pdf(path: Path) -> LoadedDocument:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise UnsupportedDocumentTypeError("PDF parsing requires the pypdf dependency") from exc

    try:
        reader = PdfReader(str(path))
        blocks: list[LoadedTextBlock] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                blocks.append(
                    LoadedTextBlock(
                        text=text,
                        page_number=index,
                        position_start=0,
                        position_end=len(text),
                        metadata={"loader": "pdf"},
                    )
                )
    except Exception as exc:
        raise DocumentLoadError(f"Failed to parse PDF: {path}") from exc

    return LoadedDocument(path=path, file_type="pdf", text_blocks=blocks)


def _load_ocr_json(path: Path) -> LoadedDocument:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DocumentLoadError(f"Invalid OCR JSON: {path}") from exc

    text_blocks = _extract_text_blocks(raw)
    table_rows = _extract_table_rows(raw)
    return LoadedDocument(
        path=path,
        file_type="json",
        text_blocks=text_blocks,
        table_rows=table_rows,
        raw_json=raw,
    )


def _extract_text_blocks(raw: Any) -> list[LoadedTextBlock]:
    blocks: list[LoadedTextBlock] = []

    if isinstance(raw, dict):
        for key in ("text", "ocr_text", "content", "plain_text"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                blocks.append(
                    LoadedTextBlock(
                        text=value,
                        page_number=_as_int(raw.get("page_number") or raw.get("page")),
                        position_start=0,
                        position_end=len(value),
                        metadata={"json_key": key},
                    )
                )

        pages = raw.get("pages")
        if isinstance(pages, list):
            for index, page in enumerate(pages, start=1):
                if isinstance(page, dict):
                    text = page.get("text") or page.get("ocr_text") or page.get("content")
                    if isinstance(text, str) and text.strip():
                        blocks.append(
                            LoadedTextBlock(
                                text=text,
                                page_number=_as_int(page.get("page_number") or page.get("page")) or index,
                                position_start=0,
                                position_end=len(text),
                                metadata={"json_key": "pages"},
                            )
                        )
                elif isinstance(page, str) and page.strip():
                    blocks.append(
                        LoadedTextBlock(
                            text=page,
                            page_number=index,
                            position_start=0,
                            position_end=len(page),
                            metadata={"json_key": "pages"},
                        )
                    )

    elif isinstance(raw, list):
        text = "\n".join(item for item in raw if isinstance(item, str) and item.strip())
        if text:
            blocks.append(
                LoadedTextBlock(text=text, position_start=0, position_end=len(text), metadata={"json_key": "root"})
            )

    return blocks


def _extract_table_rows(raw: Any) -> list[LoadedTableRow]:
    rows: list[LoadedTableRow] = []

    def add_row(value: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        row_values = value.get("values") if isinstance(value.get("values"), dict) else value
        if _looks_like_table_row(row_values):
            rows.append(
                LoadedTableRow(
                    values=dict(row_values),
                    page_number=_as_int(value.get("page_number") or value.get("page")),
                    source_image_path=_as_str(value.get("source_image_path") or value.get("image_path")),
                    metadata=metadata or {},
                )
            )

    def add_rows(value: Any, metadata: dict[str, Any] | None = None) -> None:
        if isinstance(value, dict):
            add_row(value, metadata)
        elif isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                for item in value:
                    add_row(item, metadata)
            elif value and all(isinstance(item, list) for item in value):
                rows.extend(_rows_from_matrix(value, metadata or {}))

    if isinstance(raw, dict):
        for key in ("tables", "table_records", "records", "rows"):
            value = raw.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and isinstance(item.get("rows"), list):
                        add_rows(item["rows"], {"json_key": key, "table_title": item.get("title")})
                    else:
                        add_rows(item, {"json_key": key})

        pages = raw.get("pages")
        if isinstance(pages, list):
            for page_index, page in enumerate(pages, start=1):
                if not isinstance(page, dict):
                    continue
                page_number = _as_int(page.get("page_number") or page.get("page")) or page_index
                for key in ("tables", "table_records", "records", "rows"):
                    value = page.get(key)
                    if not isinstance(value, list):
                        continue
                    before = len(rows)
                    for item in value:
                        if isinstance(item, dict) and isinstance(item.get("rows"), list):
                            add_rows(item["rows"], {"json_key": f"pages.{key}", "table_title": item.get("title")})
                        else:
                            add_rows(item, {"json_key": f"pages.{key}"})
                    for row in rows[before:]:
                        if row.page_number is None:
                            row.metadata["page_number"] = page_number

    elif isinstance(raw, list):
        add_rows(raw, {"json_key": "root"})

    return rows


def _rows_from_matrix(matrix: list[Any], metadata: dict[str, Any]) -> list[LoadedTableRow]:
    if len(matrix) < 2 or not all(isinstance(item, list) for item in matrix):
        return []
    headers = [str(item).strip() for item in matrix[0]]
    rows: list[LoadedTableRow] = []
    for values in matrix[1:]:
        mapped = {headers[index]: values[index] for index in range(min(len(headers), len(values)))}
        if _looks_like_table_row(mapped):
            rows.append(LoadedTableRow(values=mapped, metadata=dict(metadata)))
    return rows


def _looks_like_table_row(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    keys = {str(key).strip().lower() for key in value.keys()}
    markers = {
        "院校",
        "学校",
        "专业",
        "研究方向",
        "考试科目",
        "分数线",
        "招生人数",
        "school",
        "university",
        "major",
        "exam_subjects",
        "subjects",
        "score_line",
        "enrollment_count",
    }
    return bool(keys & markers)


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
