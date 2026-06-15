from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceInfo:
    file_name: str
    file_path: str
    source: str | None = None
    source_type: str = "uploaded"
    source_url: str | None = None
    page_number: int | None = None
    position_start: int | None = None
    position_end: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def as_metadata(self) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "file_name": self.file_name,
            "file_path": self.file_path,
            "source": self.source,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "page_number": self.page_number,
            "position_start": self.position_start,
            "position_end": self.position_end,
        }
        metadata.update(self.extra)
        return {key: value for key, value in metadata.items() if value is not None}


@dataclass(frozen=True)
class ChunkRecord:
    content: str
    chunk_type: str = "text"
    token_count: int = 0
    page_number: int | None = None
    position_start: int | None = None
    position_end: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
