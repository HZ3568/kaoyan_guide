from __future__ import annotations

import re
from typing import Any

from app.ingestion.loaders import LoadedDocument, LoadedTableRow, LoadedTextBlock
from app.rag.chunk_schema import ChunkRecord, SourceInfo


FIELD_ALIASES = {
    "school": ("院校", "学校", "招生单位", "school", "university", "college"),
    "major": ("专业", "专业名称", "major", "program"),
    "research_direction": ("研究方向", "方向", "research_direction", "direction"),
    "exam_subjects": ("考试科目", "科目", "初试科目", "exam_subjects", "subjects"),
    "score_line": ("分数线", "复试线", "国家线", "score_line", "score"),
    "enrollment_count": ("招生人数", "拟招生人数", "统招人数", "enrollment_count", "quota"),
    "note": ("备注", "说明", "note", "remark"),
}

TABLE_LABELS = {
    "school": "院校",
    "major": "专业",
    "research_direction": "研究方向",
    "exam_subjects": "考试科目",
    "score_line": "分数线",
    "enrollment_count": "招生人数",
    "note": "备注",
}


def chunk_loaded_document(
    loaded: LoadedDocument,
    source_info: SourceInfo,
    *,
    max_tokens: int = 800,
    overlap_tokens: int = 80,
) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    for block in loaded.text_blocks:
        chunks.extend(chunk_text_block(block, source_info, max_tokens=max_tokens, overlap_tokens=overlap_tokens))

    for row_index, row in enumerate(loaded.table_rows):
        chunks.append(chunk_table_row(row, source_info, row_index=row_index))

    for index, chunk in enumerate(chunks):
        metadata = dict(chunk.metadata)
        metadata["chunk_index"] = index
        chunks[index] = ChunkRecord(
            content=chunk.content,
            chunk_type=chunk.chunk_type,
            token_count=chunk.token_count,
            page_number=chunk.page_number,
            position_start=chunk.position_start,
            position_end=chunk.position_end,
            metadata=metadata,
        )
    return chunks


def chunk_text_block(
    block: LoadedTextBlock,
    source_info: SourceInfo,
    *,
    max_tokens: int = 800,
    overlap_tokens: int = 80,
) -> list[ChunkRecord]:
    text = clean_text(block.text)
    if not text:
        return []

    paragraphs = _paragraphs_with_offsets(text)
    chunks: list[ChunkRecord] = []
    current_parts: list[tuple[str, int, int]] = []
    current_tokens = 0

    def flush() -> None:
        nonlocal current_parts, current_tokens
        if not current_parts:
            return
        content = "\n\n".join(part[0] for part in current_parts).strip()
        start = current_parts[0][1]
        end = current_parts[-1][2]
        chunks.append(_text_chunk(content, block, source_info, start, end))

        if overlap_tokens > 0:
            overlap_parts: list[tuple[str, int, int]] = []
            overlap_count = 0
            for part in reversed(current_parts):
                part_tokens = estimate_tokens(part[0])
                if overlap_parts and overlap_count + part_tokens > overlap_tokens:
                    break
                overlap_parts.insert(0, part)
                overlap_count += part_tokens
            current_parts = overlap_parts
            current_tokens = overlap_count
        else:
            current_parts = []
            current_tokens = 0

    for paragraph, start, end in paragraphs:
        paragraph_tokens = estimate_tokens(paragraph)
        if paragraph_tokens > max_tokens:
            flush()
            for segment, segment_start, segment_end in _split_long_paragraph(paragraph, start, max_tokens):
                chunks.append(_text_chunk(segment, block, source_info, segment_start, segment_end))
            current_parts = []
            current_tokens = 0
            continue

        if current_parts and current_tokens + paragraph_tokens > max_tokens:
            flush()

        current_parts.append((paragraph, start, end))
        current_tokens += paragraph_tokens

    flush()
    return chunks


def chunk_table_row(row: LoadedTableRow, source_info: SourceInfo, *, row_index: int) -> ChunkRecord:
    normalized = normalize_table_fields(row.values)
    lines = [
        f"{TABLE_LABELS[key]}：{value}"
        for key, value in normalized.items()
        if key in TABLE_LABELS and value not in (None, "")
    ]
    if not lines:
        lines = [f"{key}：{value}" for key, value in row.values.items() if value not in (None, "")]

    content = "\n".join(lines)
    page_number = row.page_number or _as_int(row.metadata.get("page_number")) or source_info.page_number
    metadata = source_info.as_metadata()
    metadata.update(
        {
            "chunk_type": "table",
            "row_index": row_index,
            "table_fields": normalized,
            "raw_row": row.values,
            "source_image_path": row.source_image_path,
            **row.metadata,
        }
    )
    metadata = {key: value for key, value in metadata.items() if value is not None}

    return ChunkRecord(
        content=content,
        chunk_type="table",
        token_count=estimate_tokens(content),
        page_number=page_number,
        metadata=metadata,
    )


def normalize_table_fields(row: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    lower_to_key = {str(key).strip().lower(): key for key in row.keys()}
    raw_to_key = {str(key).strip(): key for key in row.keys()}

    for canonical, aliases in FIELD_ALIASES.items():
        value = None
        for alias in aliases:
            key = raw_to_key.get(alias) or lower_to_key.get(alias.lower())
            if key is not None:
                value = row.get(key)
                break
        if value is not None:
            normalized[canonical] = value
    return normalized


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def estimate_tokens(text: str) -> int:
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z0-9_]+", text))
    punctuation = len(re.findall(r"[^\w\s\u4e00-\u9fff]", text))
    return cjk_chars + words + max(1, punctuation // 4)


def _paragraphs_with_offsets(text: str) -> list[tuple[str, int, int]]:
    paragraphs: list[tuple[str, int, int]] = []
    pattern = re.compile(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", re.S)
    for match in pattern.finditer(text):
        paragraph = match.group(0).strip()
        if paragraph:
            paragraphs.append((paragraph, match.start(), match.end()))
    if not paragraphs and text.strip():
        paragraphs.append((text.strip(), 0, len(text)))
    return paragraphs


def _split_long_paragraph(paragraph: str, base_start: int, max_tokens: int) -> list[tuple[str, int, int]]:
    sentences = re.split(r"(?<=[。！？.!?])\s*", paragraph)
    segments: list[tuple[str, int, int]] = []
    current = ""
    current_start = base_start
    cursor = 0

    for sentence in [item for item in sentences if item]:
        sentence_start = paragraph.find(sentence, cursor)
        if sentence_start < 0:
            sentence_start = cursor
        absolute_start = base_start + sentence_start
        sentence_tokens = estimate_tokens(sentence)

        if sentence_tokens > max_tokens:
            if current:
                segments.append((current.strip(), current_start, current_start + len(current)))
                current = ""
            segments.extend(_split_by_width(sentence, absolute_start, max_tokens))
        elif current and estimate_tokens(current) + sentence_tokens > max_tokens:
            segments.append((current.strip(), current_start, current_start + len(current)))
            current = sentence
            current_start = absolute_start
        else:
            if not current:
                current_start = absolute_start
            current = f"{current}{sentence}"

        cursor = sentence_start + len(sentence)

    if current.strip():
        segments.append((current.strip(), current_start, current_start + len(current)))
    return segments


def _split_by_width(text: str, base_start: int, max_tokens: int) -> list[tuple[str, int, int]]:
    width = max(200, max_tokens)
    segments: list[tuple[str, int, int]] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + width)
        segment = text[start:end].strip()
        if segment:
            segments.append((segment, base_start + start, base_start + end))
        start = end
    return segments


def _text_chunk(
    content: str,
    block: LoadedTextBlock,
    source_info: SourceInfo,
    position_start: int,
    position_end: int,
) -> ChunkRecord:
    page_number = block.page_number or source_info.page_number
    metadata = source_info.as_metadata()
    metadata.update(
        {
            "chunk_type": "text",
            "page_number": page_number,
            "position_start": position_start,
            "position_end": position_end,
            **block.metadata,
        }
    )
    metadata = {key: value for key, value in metadata.items() if value is not None}
    return ChunkRecord(
        content=content,
        chunk_type="text",
        token_count=estimate_tokens(content),
        page_number=page_number,
        position_start=position_start,
        position_end=position_end,
        metadata=metadata,
    )


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
