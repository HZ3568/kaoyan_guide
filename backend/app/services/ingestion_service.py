from app.ingestion.chunkers import clean_text
from app.ingestion.loaders import UnsupportedDocumentTypeError, load_document
from app.ingestion.pipeline import content_hash


class IngestionService:
    """兼容旧调用的基础解析服务；新导入流程使用 app.ingestion.pipeline。"""

    def parse_file(self, file_path: str) -> str:
        loaded = load_document(file_path)
        texts = [block.text for block in loaded.text_blocks]
        for row in loaded.table_rows:
            texts.append(" ".join(str(value) for value in row.values.values() if value is not None))
        return "\n\n".join(texts)

    def clean_text(self, text: str) -> str:
        return clean_text(text)

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
        return [chunk for chunk in chunks if chunk]

    @staticmethod
    def content_hash(content: str) -> str:
        return content_hash(content)
