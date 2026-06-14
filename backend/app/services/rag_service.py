from sqlalchemy.orm import Session

from app.schemas.rag import ChatResponse, Citation, RetrievalFilter
from app.services.retrieval_service import RetrievalService


class RagService:
    def __init__(self, db: Session) -> None:
        self.retrieval = RetrievalService(db)

    def chat(
        self,
        question: str,
        user_id: int,
        filters: RetrievalFilter | None = None,
    ) -> ChatResponse:
        chunks = self.retrieval.retrieve(question, top_k=5, user_id=user_id, filters=filters)
        if not chunks:
            return ChatResponse(
                answer="资料库中没有找到充分依据。请先上传相关考研资料，或缩小问题范围。",
                confidence=0.0,
                retrieval_debug={"reason": "no_chunks"},
            )

        context_preview = "\n\n".join([f"[{i+1}] {c.content[:300]}" for i, c in enumerate(chunks)])
        answer = (
            "以下是基于当前知识库检索结果的初步回答：\n\n"
            f"问题：{question}\n\n"
            "相关资料摘要：\n"
            f"{context_preview}\n\n"
            "说明：当前 LLM Provider 仍是 mock，占位回答用于跑通 RAG 流程。后续可在 rag_service 中接入真实大模型。"
        )
        citations = [
            Citation(
                document_id=c.document_id,
                chunk_id=c.chunk_id,
                document_title=c.metadata.get("title"),
                content_preview=c.content[:120],
            )
            for c in chunks
        ]
        return ChatResponse(
            answer=answer,
            citations=citations,
            confidence=0.5,
            retrieval_debug={"top_k": len(chunks), "mode": "keyword_placeholder"},
        )
