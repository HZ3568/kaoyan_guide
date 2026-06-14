import hashlib
import re
from pathlib import Path


class UnsupportedDocumentTypeError(ValueError):
    pass


class IngestionService:
    """基础解析服务。后续可扩展 PDF、Word、OCR、表格解析。"""

    TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".json"}
    UNSUPPORTED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".tif",
        ".tiff",
    }

    def parse_file(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in self.TEXT_EXTENSIONS:
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix in self.UNSUPPORTED_EXTENSIONS:
            raise UnsupportedDocumentTypeError(f"Unsupported document type: {suffix}")
        raise UnsupportedDocumentTypeError(f"Unsupported document type: {suffix or 'unknown'}")

    def clean_text(self, text: str) -> str:
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def split_chunks(self, text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
        text = self.clean_text(text)
        if not text:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end].strip())
            if end == len(text):
                break
            start = max(0, end - overlap)
        return [c for c in chunks if c]

    @staticmethod
    def content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
