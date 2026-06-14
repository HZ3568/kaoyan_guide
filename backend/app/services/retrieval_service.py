import re

from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.schemas.rag import RetrievalFilter, RetrievedChunk
from app.services.embedding_service import get_embedding_provider


class RetrievalService:
    """第一版检索服务。

    当前使用关键词粗召回占位，后续替换为 Redis Vector + BM25 + Rerank。
    """

    STOP_TERMS = {
        "怎么",
        "如何",
        "复习",
        "学习",
        "备考",
        "资料",
        "重点",
        "计划",
        "应该",
        "什么",
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_provider = get_embedding_provider()

    @staticmethod
    def _query_terms(query: str) -> list[str]:
        query_lower = query.lower().strip()
        terms = [t for t in query_lower.split() if t]
        for phrase in re.findall(r"[\u4e00-\u9fff]{2,}", query_lower):
            terms.extend(phrase[i : i + 2] for i in range(len(phrase) - 1))
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
        chunks_query = self.db.query(DocumentChunk).join(Document, Document.id == DocumentChunk.document_id)
        if user_id is not None:
            chunks_query = chunks_query.filter(Document.user_id == user_id)
        if filters:
            if filters.subject:
                chunks_query = chunks_query.filter(Document.subject == filters.subject)
            if filters.school:
                chunks_query = chunks_query.filter(Document.school == filters.school)
            if filters.major:
                chunks_query = chunks_query.filter(Document.major == filters.major)
            if filters.year:
                chunks_query = chunks_query.filter(Document.exam_year == filters.year)

        chunks = chunks_query.limit(200).all()
        scored = []
        for chunk in chunks:
            content_lower = chunk.content.lower()
            score = sum(1 for term in query_terms if term in content_lower)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            RetrievedChunk(
                chunk_id=c.id,
                document_id=c.document_id,
                content=c.content,
                score=float(score),
                metadata=c.metadata_json or {},
            )
            for score, c in scored[:top_k]
        ]
