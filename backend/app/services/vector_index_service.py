from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.rag.vector_store import RedisVectorHit, RedisVectorStore, VectorStoreError
from app.schemas.rag import RetrievalFilter
from app.services.embedding_service import EmbeddingError, EmbeddingProvider, get_embedding_provider


@dataclass
class VectorIndexResult:
    indexed: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)
    index_name: str = ""
    embedding_dim: int = 0


@dataclass
class VectorSearchResult:
    chunk_id: int
    document_id: int
    score: float
    content: str
    source: dict[str, Any]
    page_number: int | None
    location: dict[str, int | None]
    metadata: dict[str, Any]


class VectorIndexService:
    def __init__(
        self,
        db: Session,
        *,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: RedisVectorStore | None = None,
    ) -> None:
        self.db = db
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.vector_store = vector_store or RedisVectorStore(dim=self.embedding_provider.dim)

    def index_pending(
        self,
        *,
        user_id: int,
        document_id: int | None = None,
        limit: int = 100,
        batch_size: int = 32,
        force_reindex: bool = False,
    ) -> VectorIndexResult:
        self.vector_store.ensure_index()
        result = VectorIndexResult(
            index_name=self.vector_store.index_name,
            embedding_dim=self.embedding_provider.dim,
        )
        chunks = self._chunks_for_indexing(
            user_id=user_id,
            document_id=document_id,
            limit=limit,
            force_reindex=force_reindex,
        )
        if not chunks:
            result.skipped = 0
            return result

        safe_batch_size = max(1, batch_size)
        for start in range(0, len(chunks), safe_batch_size):
            batch = chunks[start : start + safe_batch_size]
            try:
                embeddings = self.embedding_provider.embed_documents([chunk.content for chunk in batch])
            except EmbeddingError as exc:
                self._mark_batch_failed(batch, str(exc))
                result.failed += len(batch)
                result.errors.append(str(exc))
                continue

            if len(embeddings) != len(batch):
                message = f"Embedding provider returned {len(embeddings)} vectors for {len(batch)} chunks"
                self._mark_batch_failed(batch, message)
                result.failed += len(batch)
                result.errors.append(message)
                continue

            for chunk, embedding in zip(batch, embeddings, strict=True):
                try:
                    self._index_chunk(chunk, embedding)
                    result.indexed += 1
                except (EmbeddingError, VectorStoreError, ValueError) as exc:
                    chunk.embedding_status = "failed"
                    result.failed += 1
                    result.errors.append(f"chunk {chunk.id}: {exc}")
            self.db.commit()
        return result

    def search(
        self,
        *,
        query: str,
        user_id: int,
        top_k: int = 5,
        filters: RetrievalFilter | None = None,
    ) -> list[VectorSearchResult]:
        embedding = self.embedding_provider.embed_query(query)
        redis_hits = self.vector_store.search(
            embedding=embedding,
            top_k=min(max(top_k * 5, top_k), 100),
            user_id=user_id,
            filters={},
        )
        if not redis_hits:
            return []
        chunks_by_id = self._load_authorized_chunks(redis_hits, user_id=user_id, filters=filters)
        results: list[VectorSearchResult] = []
        for hit in redis_hits:
            chunk = chunks_by_id.get(hit.chunk_id)
            if not chunk:
                continue
            results.append(
                VectorSearchResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    score=hit.score,
                    content=chunk.content,
                    source=self._source_for_chunk(chunk),
                    page_number=chunk.page_number,
                    location={
                        "position_start": chunk.position_start,
                        "position_end": chunk.position_end,
                    },
                    metadata=chunk.metadata_json or {},
                )
            )
        return results[:top_k]

    def status(self, *, user_id: int) -> dict[str, Any]:
        base_query = self.db.query(DocumentChunk).join(Document, Document.id == DocumentChunk.document_id)
        base_query = base_query.filter(Document.user_id == user_id)
        total_chunks = base_query.count()
        indexed_chunks = base_query.filter(DocumentChunk.is_vectorized.is_(True)).count()
        pending_chunks = base_query.filter(DocumentChunk.embedding_status == "pending").count()
        failed_chunks = base_query.filter(DocumentChunk.embedding_status == "failed").count()
        return {
            "total_chunks": total_chunks,
            "indexed_chunks": indexed_chunks,
            "pending_chunks": pending_chunks,
            "failed_chunks": failed_chunks,
            "redis": self.vector_store.index_info(),
        }

    def _chunks_for_indexing(
        self,
        *,
        user_id: int,
        document_id: int | None,
        limit: int,
        force_reindex: bool,
    ) -> list[DocumentChunk]:
        query = (
            self.db.query(DocumentChunk)
            .options(joinedload(DocumentChunk.document))
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(Document.user_id == user_id)
        )
        if document_id is not None:
            query = query.filter(DocumentChunk.document_id == document_id)
        if not force_reindex:
            query = query.filter(
                or_(
                    DocumentChunk.is_vectorized.is_(False),
                    DocumentChunk.embedding_status.in_(["pending", "failed"]),
                )
            )
        return query.order_by(DocumentChunk.id.asc()).limit(max(1, limit)).all()

    def _index_chunk(self, chunk: DocumentChunk, embedding: list[float]) -> None:
        document = chunk.document
        metadata = self._metadata_for_redis(chunk)
        key = self.vector_store.upsert_chunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            user_id=document.user_id if document else None,
            embedding=embedding,
            content_preview=chunk.content,
            metadata=metadata,
            source=document.source if document else None,
            subject=document.subject if document else None,
            school=document.school if document else None,
            major=document.major if document else None,
            exam_year=document.exam_year if document else None,
            chunk_type=chunk.chunk_type,
        )
        chunk.embedding_status = "indexed"
        chunk.is_vectorized = True
        chunk.vector_index_key = key

    def _mark_batch_failed(self, chunks: list[DocumentChunk], message: str) -> None:
        for chunk in chunks:
            chunk.embedding_status = "failed"
            metadata = dict(chunk.metadata_json or {})
            metadata["embedding_error"] = message
            chunk.metadata_json = metadata
        self.db.commit()

    def _load_authorized_chunks(
        self,
        redis_hits: list[RedisVectorHit],
        *,
        user_id: int,
        filters: RetrievalFilter | None,
    ) -> dict[int, DocumentChunk]:
        chunk_ids = [hit.chunk_id for hit in redis_hits]
        query = (
            self.db.query(DocumentChunk)
            .options(joinedload(DocumentChunk.document))
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(DocumentChunk.id.in_(chunk_ids))
            .filter(Document.user_id == user_id)
        )
        if filters:
            if filters.subject:
                query = query.filter(Document.subject == filters.subject)
            if filters.school:
                query = query.filter(Document.school == filters.school)
            if filters.major:
                query = query.filter(Document.major == filters.major)
            if filters.year:
                query = query.filter(Document.exam_year == filters.year)
        return {chunk.id: chunk for chunk in query.all()}

    def _source_for_chunk(self, chunk: DocumentChunk) -> dict[str, Any]:
        document = chunk.document
        if not document:
            return {"document_id": chunk.document_id}
        return {
            "document_id": document.id,
            "title": document.title,
            "source": document.source,
            "source_type": document.source_type,
            "source_url": document.source_url,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "page_number": chunk.page_number,
            "position_start": chunk.position_start,
            "position_end": chunk.position_end,
        }

    def _metadata_for_redis(self, chunk: DocumentChunk) -> dict[str, Any]:
        document = chunk.document
        metadata = dict(chunk.metadata_json or {})
        metadata.update(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "chunk_type": chunk.chunk_type,
                "page_number": chunk.page_number,
                "position_start": chunk.position_start,
                "position_end": chunk.position_end,
                "token_count": chunk.token_count,
            }
        )
        if document:
            metadata.update(
                {
                    "title": document.title,
                    "source": document.source,
                    "source_type": document.source_type,
                    "source_url": document.source_url,
                    "file_name": document.file_name,
                    "file_type": document.file_type,
                    "subject": document.subject,
                    "school": document.school,
                    "major": document.major,
                    "exam_year": document.exam_year,
                    "tags": document.tags_json or [],
                }
            )
        return metadata
