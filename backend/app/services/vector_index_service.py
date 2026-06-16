from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.rag.vector_store import RedisVectorHit, RedisVectorStore, VectorStoreError
from app.schemas.rag import RetrievalFilter
from app.services.embedding_service import (
    DIMENSION_REBUILD_NOTICE,
    EmbeddingError,
    EmbeddingProvider,
    embedding_runtime_config,
    get_embedding_provider,
)


@dataclass
class VectorIndexResult:
    indexed: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)
    index_name: str = ""
    embedding_dim: int = 0
    dimension_notice: str = DIMENSION_REBUILD_NOTICE


@dataclass
class VectorSearchResult:
    chunk_id: int
    document_id: int
    score: float
    content: str
    source: dict[str, Any]
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
        knowledge_base_id: int | None = None,
        goal_id: int | None = None,
        limit: int = 100,
        batch_size: int = 32,
        force_reindex: bool = False,
    ) -> VectorIndexResult:
        self.vector_store.ensure_index()
        result = VectorIndexResult(index_name=self.vector_store.index_name, embedding_dim=self.embedding_provider.dim)
        chunks = self._chunks_for_indexing(
            user_id=user_id,
            document_id=document_id,
            knowledge_base_id=knowledge_base_id,
            goal_id=goal_id,
            limit=limit,
            force_reindex=force_reindex,
        )
        if not chunks:
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
            self._refresh_document_embedding_status(batch)
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
        filter_dict = filters.model_dump(exclude_none=True) if filters else {}
        embedding = self.embedding_provider.embed_query(query)
        redis_hits = self.vector_store.search(
            embedding=embedding,
            top_k=min(max(top_k * 5, top_k), 100),
            user_id=user_id,
            filters=filter_dict,
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
                    metadata=chunk.metadata_json or {},
                )
            )
        return results[:top_k]

    def status(self, *, user_id: int) -> dict[str, Any]:
        base_query = self.db.query(DocumentChunk).filter(DocumentChunk.user_id == user_id)
        total_chunks = base_query.count()
        indexed_chunks = base_query.filter(DocumentChunk.embedding_status == "indexed").count()
        pending_chunks = base_query.filter(DocumentChunk.embedding_status == "pending").count()
        failed_chunks = base_query.filter(DocumentChunk.embedding_status == "failed").count()
        return {
            "total_chunks": total_chunks,
            "indexed_chunks": indexed_chunks,
            "pending_chunks": pending_chunks,
            "failed_chunks": failed_chunks,
            "redis": self.vector_store.index_info(),
            "embedding": embedding_runtime_config(),
            "dimension_notice": DIMENSION_REBUILD_NOTICE,
        }

    def _chunks_for_indexing(
        self,
        *,
        user_id: int,
        document_id: int | None,
        knowledge_base_id: int | None,
        goal_id: int | None,
        limit: int,
        force_reindex: bool,
    ) -> list[DocumentChunk]:
        query = (
            self.db.query(DocumentChunk)
            .options(joinedload(DocumentChunk.document))
            .filter(DocumentChunk.user_id == user_id)
        )
        if document_id is not None:
            query = query.filter(DocumentChunk.document_id == document_id)
        if knowledge_base_id is not None:
            query = query.filter(DocumentChunk.knowledge_base_id == knowledge_base_id)
        if goal_id is not None:
            query = query.filter(DocumentChunk.goal_id == goal_id)
        if not force_reindex:
            query = query.filter(DocumentChunk.embedding_status.in_(["pending", "failed"]))
        return query.order_by(DocumentChunk.id.asc()).limit(max(1, limit)).all()

    def _index_chunk(self, chunk: DocumentChunk, embedding: list[float]) -> None:
        metadata = self._metadata_for_redis(chunk)
        key = self.vector_store.upsert_chunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            user_id=chunk.user_id,
            goal_id=chunk.goal_id,
            knowledge_base_id=chunk.knowledge_base_id,
            domain=chunk.domain,
            category=chunk.category,
            embedding=embedding,
            content_preview=chunk.content,
            metadata=metadata,
        )
        chunk.embedding_status = "indexed"
        chunk.embedding_id = key
        if chunk.document:
            chunk.document.embedding_status = "indexed"

    def _mark_batch_failed(self, chunks: list[DocumentChunk], message: str) -> None:
        for chunk in chunks:
            chunk.embedding_status = "failed"
            metadata = dict(chunk.metadata_json or {})
            metadata["embedding_error"] = message
            chunk.metadata_json = metadata
            if chunk.document:
                chunk.document.embedding_status = "failed"
        self.db.commit()

    def _refresh_document_embedding_status(self, chunks: list[DocumentChunk]) -> None:
        document_ids = {chunk.document_id for chunk in chunks}
        for document_id in document_ids:
            statuses = {
                status
                for (status,) in self.db.query(DocumentChunk.embedding_status)
                .filter(DocumentChunk.document_id == document_id)
                .all()
            }
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if not document:
                continue
            if statuses == {"indexed"}:
                document.embedding_status = "indexed"
            elif "failed" in statuses:
                document.embedding_status = "partial_failed"
            else:
                document.embedding_status = "pending"

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
            .filter(DocumentChunk.id.in_(chunk_ids), DocumentChunk.user_id == user_id)
        )
        if filters:
            if filters.goal_id is not None:
                query = query.filter(DocumentChunk.goal_id == filters.goal_id)
            if filters.knowledge_base_id is not None:
                query = query.filter(DocumentChunk.knowledge_base_id == filters.knowledge_base_id)
            if filters.domain:
                query = query.filter(DocumentChunk.domain == filters.domain)
            if filters.category:
                query = query.filter(DocumentChunk.category == filters.category)
        return {chunk.id: chunk for chunk in query.all()}

    def _source_for_chunk(self, chunk: DocumentChunk) -> dict[str, Any]:
        document = chunk.document
        return {
            "knowledge_base_id": chunk.knowledge_base_id,
            "goal_id": chunk.goal_id,
            "filename": document.filename if document else None,
            "original_filename": document.original_filename if document else None,
            "domain": chunk.domain,
            "category": chunk.category,
        }

    def _metadata_for_redis(self, chunk: DocumentChunk) -> dict[str, Any]:
        document = chunk.document
        metadata = dict(chunk.metadata_json or {})
        metadata.update(
            {
                "user_id": chunk.user_id,
                "goal_id": chunk.goal_id,
                "knowledge_base_id": chunk.knowledge_base_id,
                "document_id": chunk.document_id,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "domain": chunk.domain,
                "category": chunk.category,
            }
        )
        if document:
            metadata.update(
                {
                    "filename": document.filename,
                    "original_filename": document.original_filename,
                    "file_type": document.file_type,
                }
            )
        return metadata
