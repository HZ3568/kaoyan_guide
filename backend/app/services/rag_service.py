from time import perf_counter

from sqlalchemy.orm import Session

from app.llm.client import LLMClient, LLMMessage, get_llm_client
from app.models.rag_log import RagQueryLog
from app.schemas.rag import RagAskResponse, RagSource, RetrievalFilter
from app.services.vector_index_service import VectorIndexService, VectorSearchResult


SYSTEM_PROMPT = """你是一个基于用户私有知识库回答问题的学习助手。
你必须只依据检索到的 context 回答。
如果 context 中没有可靠依据，请直接说明当前知识库没有找到可靠依据。
回答中需要标注来源编号。
不要编造不存在的数据、政策、岗位要求、考试要求、技术细节或文档结论。
如果资料之间存在冲突，请说明冲突，并分别给出来源。"""

NO_EVIDENCE_ANSWER = "当前知识库没有找到可靠依据。"


class RagService:
    def __init__(
        self,
        db: Session,
        *,
        llm_client: LLMClient | None = None,
        vector_service: VectorIndexService | None = None,
    ) -> None:
        self.db = db
        self.llm_client = llm_client or get_llm_client()
        self.vector_service = vector_service or VectorIndexService(db)

    def ask(
        self,
        question: str,
        *,
        user_id: int,
        top_k: int = 5,
        filters: RetrievalFilter | None = None,
        knowledge_base_id: int | None = None,
        goal_id: int | None = None,
        stream: bool = False,
    ) -> RagAskResponse:
        start = perf_counter()
        merged_filters = self._merge_filters(filters, knowledge_base_id=knowledge_base_id, goal_id=goal_id)
        chunks = self.vector_service.search(
            query=question,
            user_id=user_id,
            top_k=top_k,
            filters=merged_filters,
        )
        if not chunks:
            log_id = self._write_log(
                user_id=user_id,
                goal_id=merged_filters.goal_id if merged_filters else None,
                knowledge_base_id=merged_filters.knowledge_base_id if merged_filters else None,
                question=question,
                top_k=top_k,
                filters=merged_filters,
                sources=[],
                answer=NO_EVIDENCE_ANSWER,
            )
            return RagAskResponse(
                answer=NO_EVIDENCE_ANSWER,
                sources=[],
                hit_source=False,
                model_provider=None,
                model_name=None,
                log_id=log_id,
                retrieval_debug={
                    "top_k": top_k,
                    "retrieved": 0,
                    "mode": "vector_rag",
                    "llm_called": False,
                    "latency_ms": self._elapsed_ms(start),
                },
            )

        messages = self._build_messages(question, chunks)
        llm_response = self.llm_client.generate(messages)
        sources = [self._source_from_result(index, chunk) for index, chunk in enumerate(chunks, start=1)]
        log_id = self._write_log(
            user_id=user_id,
            goal_id=merged_filters.goal_id if merged_filters else None,
            knowledge_base_id=merged_filters.knowledge_base_id if merged_filters else None,
            question=question,
            top_k=top_k,
            filters=merged_filters,
            sources=[source.model_dump() for source in sources],
            answer=llm_response.content,
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
                "llm_called": True,
                "latency_ms": self._elapsed_ms(start),
            },
        )

    def _build_messages(self, question: str, chunks: list[VectorSearchResult]) -> list[LLMMessage]:
        context_blocks: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            source = chunk.source
            filename = source.get("original_filename") or source.get("filename") or f"document:{chunk.document_id}"
            context_blocks.append(
                f"[来源{index}]\n"
                f"{chunk.content}\n"
                f"[来源{index}] chunk_id={chunk.chunk_id}; document_id={chunk.document_id}; "
                f"filename={filename}; domain={source.get('domain') or ''}; category={source.get('category') or ''}"
            )
        context_text = "\n\n".join(context_blocks)
        user_prompt = (
            f"用户问题：\n{question.strip()}\n\n"
            f"检索上下文：\n{context_text}\n\n"
            "回答要求：\n"
            "1. 只根据检索上下文回答。\n"
            "2. 涉及具体事实、要求、结论或步骤时，在句末标注来源编号，例如 [来源1]。\n"
            "3. 如果上下文没有依据，回答“当前知识库没有找到可靠依据”。\n"
            "4. 不要补充上下文之外的事实。"
        )
        return [
            LLMMessage(role="system", content=SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

    @staticmethod
    def _merge_filters(
        filters: RetrievalFilter | None,
        *,
        knowledge_base_id: int | None,
        goal_id: int | None,
    ) -> RetrievalFilter | None:
        data = filters.model_dump(exclude_none=True) if filters else {}
        if knowledge_base_id is not None:
            data["knowledge_base_id"] = knowledge_base_id
        if goal_id is not None:
            data["goal_id"] = goal_id
        return RetrievalFilter(**data) if data else None

    @staticmethod
    def _source_from_result(index: int, chunk: VectorSearchResult) -> RagSource:
        source = chunk.source
        return RagSource(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            knowledge_base_id=source.get("knowledge_base_id"),
            goal_id=source.get("goal_id"),
            score=chunk.score,
            filename=source.get("filename"),
            original_filename=source.get("original_filename"),
            domain=source.get("domain"),
            category=source.get("category"),
            content_preview=chunk.content[:200],
            metadata={**chunk.metadata, "source_index": index},
        )

    def _write_log(
        self,
        *,
        user_id: int,
        goal_id: int | None,
        knowledge_base_id: int | None,
        question: str,
        top_k: int,
        filters: RetrievalFilter | None,
        sources: list[dict],
        answer: str,
    ) -> int:
        log = RagQueryLog(
            user_id=user_id,
            goal_id=goal_id,
            knowledge_base_id=knowledge_base_id,
            question=question,
            answer=answer,
            top_k=top_k,
            filters_json=filters.model_dump(exclude_none=True) if filters else None,
            sources_json=sources,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log.id

    @staticmethod
    def _elapsed_ms(start: float) -> int:
        return int((perf_counter() - start) * 1000)
