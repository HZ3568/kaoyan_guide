import re
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.schemas.rag import RetrievalFilter
from app.services.embedding_service import get_embedding_provider


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int | None
    content: str
    score: float
    metadata: dict = field(default_factory=dict)


class RetrievalService:
    """Small keyword fallback retriever for local diagnostics."""

    STOP_TERMS = {"怎么", "如何", "学习", "资料", "重点", "计划", "应该", "什么"}

    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_provider = get_embedding_provider()

    @staticmethod
    def _query_terms(query: str) -> list[str]:
        query_lower = query.lower().strip()
        terms = [item for item in query_lower.split() if item]
        for phrase in re.findall(r"[\u4e00-\u9fff]{2,}", query_lower):
            terms.extend(phrase[index : index + 2] for index in range(len(phrase) - 1))
        return [term for term in dict.fromkeys(terms) if term not in RetrievalService.STOP_TERMS]

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        user_id: int | None = None,
        filters: RetrievalFilter | None = None,
    ) -> list[RetrievedChunk]:
        _ = self.embedding_provider.embed_query(query)
        query_terms = self._query_terms(query)
        if not query_terms:
            return []
        chunks_query = self.db.query(DocumentChunk)
        if user_id is not None:
            chunks_query = chunks_query.filter(DocumentChunk.user_id == user_id)
        if filters:
            if filters.goal_id is not None:
                chunks_query = chunks_query.filter(DocumentChunk.goal_id == filters.goal_id)
            if filters.knowledge_base_id is not None:
                chunks_query = chunks_query.filter(DocumentChunk.knowledge_base_id == filters.knowledge_base_id)
            if filters.domain:
                chunks_query = chunks_query.filter(DocumentChunk.domain == filters.domain)
            if filters.category:
                chunks_query = chunks_query.filter(DocumentChunk.category == filters.category)

        scored = []
        for chunk in chunks_query.limit(200).all():
            content_lower = chunk.content.lower()
            score = sum(1 for term in query_terms if term in content_lower)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                score=float(score),
                metadata=chunk.metadata_json or {},
            )
            for score, chunk in scored[:top_k]
        ]
