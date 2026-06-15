from time import perf_counter
from sqlalchemy.orm import Session

from app.llm.client import LLMClient, LLMMessage, get_llm_client
from app.models.rag_log import RagQueryLog
from app.schemas.rag import (
    ChatResponse,
    Citation,
    RagAskResponse,
    RagSource,
    RetrievalFilter,
)
from app.services.retrieval_service import RetrievalService
from app.services.vector_index_service import VectorIndexService, VectorSearchResult


SYSTEM_PROMPT = """你是考研资料问答助手。
你必须只根据给定的检索上下文回答问题。
涉及院校、专业、研究方向、考试科目、分数线、招生人数等事实时，必须依据上下文并引用来源编号。
如果上下文没有提供依据，必须明确说明不确定或当前知识库没有找到依据。
不要编造院校、专业、分数线、招生人数、政策时间或资料来源。"""


class RagService:
    def __init__(
        self,
        db: Session,
        *,
        llm_client: LLMClient | None = None,
        vector_service: VectorIndexService | None = None,
    ) -> None:
        self.db = db
        self.retrieval = RetrievalService(db)
        self.llm_client = llm_client or get_llm_client()
        self.vector_service = vector_service or VectorIndexService(db)

    def ask(
        self,
        question: str,
        *,
        user_id: int,
        top_k: int = 5,
        filters: RetrievalFilter | None = None,
        session_id: int | None = None,
        stream: bool = False,
    ) -> RagAskResponse:
        start = perf_counter()
        if stream:
            # API 结构预留 stream；当前阶段仍返回一次性 JSON。
            stream = False

        chunks = self.vector_service.search(
            query=question,
            user_id=user_id,
            top_k=top_k,
            filters=filters,
        )
        if not chunks:
            answer = "当前知识库没有找到依据。请先上传并向量化相关资料，或调整问题和筛选条件。"
            log_id = self._write_log(
                user_id=user_id,
                session_id=session_id,
                question=question,
                filters=filters,
                retrieved_chunks=[],
                answer=answer,
                hit_source=False,
                latency_ms=self._elapsed_ms(start),
                model_provider=self.llm_client.provider,
                model_name=self.llm_client.model,
            )
            return RagAskResponse(
                answer=answer,
                sources=[],
                hit_source=False,
                model_provider=self.llm_client.provider,
                model_name=self.llm_client.model,
                log_id=log_id,
                retrieval_debug={"top_k": top_k, "retrieved": 0, "mode": "vector_rag"},
            )

        messages = self._build_messages(question, chunks)
        llm_response = self.llm_client.generate(messages)
        sources = [self._source_from_result(chunk) for chunk in chunks]
        log_id = self._write_log(
            user_id=user_id,
            session_id=session_id,
            question=question,
            filters=filters,
            retrieved_chunks=chunks,
            answer=llm_response.content,
            hit_source=True,
            latency_ms=self._elapsed_ms(start),
            model_provider=llm_response.provider,
            model_name=llm_response.model,
        )
        return RagAskResponse(
            answer=llm_response.content,
            sources=sources,
            hit_source=True,
            model_provider=llm_response.provider,
            model_name=llm_response.model,
            log_id=log_id,
            retrieval_debug={
                "top_k": top_k,
                "retrieved": len(chunks),
                "mode": "vector_rag",
                "stream": stream,
            },
        )

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

    def _build_messages(self, question: str, chunks: list[VectorSearchResult]) -> list[LLMMessage]:
        context_blocks: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            source = chunk.source
            title = source.get("title") or f"document:{chunk.document_id}"
            page = source.get("page_number") or chunk.page_number
            location = chunk.location or {}
            source_line = (
                f"[来源{index}] chunk_id={chunk.chunk_id}; document_id={chunk.document_id}; "
                f"title={title}; source={source.get('source') or ''}; "
                f"page={page or ''}; location={location}"
            )
            context_blocks.append(f"[{index}]\n{chunk.content}\n{source_line}")
        context_text = "\n\n".join(context_blocks)
        user_prompt = (
            f"用户问题：\n{question.strip()}\n\n"
            "检索上下文：\n"
            f"{context_text}\n\n"
            "回答要求：\n"
            "1. 只根据检索上下文回答。\n"
            "2. 涉及院校、专业、分数线、招生人数、考试科目时，在句末标注来源编号，例如 [来源1]。\n"
            "3. 如果上下文没有依据，回答“当前知识库没有找到依据”。\n"
            "4. 不要补充上下文之外的事实。"
        )
        return [
            LLMMessage(role="system", content=SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

    def _source_from_result(self, chunk: VectorSearchResult) -> RagSource:
        source = chunk.source
        return RagSource(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            score=chunk.score,
            title=source.get("title"),
            source=source.get("source"),
            source_type=source.get("source_type"),
            source_url=source.get("source_url"),
            file_name=source.get("file_name"),
            page_number=source.get("page_number") or chunk.page_number,
            location=chunk.location,
            content_preview=chunk.content[:200],
            metadata=chunk.metadata,
        )

    def _write_log(
        self,
        *,
        user_id: int,
        session_id: int | None,
        question: str,
        filters: RetrievalFilter | None,
        retrieved_chunks: list[VectorSearchResult],
        answer: str,
        hit_source: bool,
        latency_ms: int,
        model_provider: str | None,
        model_name: str | None,
    ) -> int:
        log = RagQueryLog(
            user_id=user_id,
            session_id=session_id,
            question=question,
            filters_json=filters.model_dump(exclude_none=True) if filters else None,
            retrieved_chunks_json=[
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "score": chunk.score,
                    "source": chunk.source,
                    "page_number": chunk.page_number,
                    "location": chunk.location,
                    "content_preview": chunk.content[:200],
                    "metadata": chunk.metadata,
                }
                for chunk in retrieved_chunks
            ],
            model_provider=model_provider,
            model_name=model_name,
            model_answer=answer,
            hit_source=hit_source,
            latency_ms=latency_ms,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log.id

    @staticmethod
    def _elapsed_ms(start: float) -> int:
        return int((perf_counter() - start) * 1000)
