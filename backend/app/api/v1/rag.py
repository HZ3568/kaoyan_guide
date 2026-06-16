from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.llm.client import LLMError
from app.models.user import User
from app.rag.vector_store import VectorStoreError
from app.schemas.rag import (
    EmbeddingConnectivityResponse,
    RagAskRequest,
    RagAskResponse,
    RagSearchRequest,
    RagSearchResult,
    RetrievalFilter,
    VectorIndexRequest,
    VectorIndexResponse,
    VectorIndexStatus,
)
from app.services.embedding_service import EmbeddingError, check_embedding_connectivity
from app.services.rag_service import RagService
from app.services.vector_index_service import VectorIndexService

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index", response_model=VectorIndexResponse)
def index_chunks(
    payload: VectorIndexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = VectorIndexService(db).index_pending(
            user_id=current_user.id,
            document_id=payload.document_id,
            knowledge_base_id=payload.knowledge_base_id,
            goal_id=payload.goal_id,
            limit=payload.limit,
            batch_size=payload.batch_size,
            force_reindex=payload.force_reindex,
        )
    except (EmbeddingError, VectorStoreError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return VectorIndexResponse(**result.__dict__)


@router.get("/index/status", response_model=VectorIndexStatus)
def index_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return VectorIndexService(db).status(user_id=current_user.id)
    except VectorStoreError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/embedding/health", response_model=EmbeddingConnectivityResponse)
def embedding_health(current_user: User = Depends(get_current_user)):
    result = check_embedding_connectivity()
    return EmbeddingConnectivityResponse(
        ok=result.ok,
        provider=result.provider,
        base_url=result.base_url,
        model=result.model,
        dimension=result.dimension,
        status_code=result.status_code,
        message=result.message,
        error_body=result.error_body,
        hints=result.hints or [],
        dimension_notice=result.dimension_notice,
    )


@router.post("/search", response_model=list[RagSearchResult])
def search(
    payload: RagSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = _merged_filters(payload.filters, goal_id=payload.goal_id, knowledge_base_id=payload.knowledge_base_id)
    try:
        results = VectorIndexService(db).search(
            query=payload.question,
            top_k=payload.top_k,
            user_id=current_user.id,
            filters=filters,
        )
    except (EmbeddingError, VectorStoreError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return [
        RagSearchResult(
            chunk_id=item.chunk_id,
            document_id=item.document_id,
            score=item.score,
            content=item.content,
            content_preview=item.content[:200],
            metadata=item.metadata,
            **item.source,
        )
        for item in results
    ]


@router.post("/ask", response_model=RagAskResponse)
def ask(
    payload: RagAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return RagService(db).ask(
            payload.question,
            user_id=current_user.id,
            top_k=payload.top_k,
            filters=payload.filters,
            knowledge_base_id=payload.knowledge_base_id,
            goal_id=payload.goal_id,
            stream=payload.stream,
        )
    except (EmbeddingError, VectorStoreError, LLMError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


def _merged_filters(
    filters: RetrievalFilter | None,
    *,
    goal_id: int | None,
    knowledge_base_id: int | None,
) -> RetrievalFilter | None:
    data = filters.model_dump(exclude_none=True) if filters else {}
    if goal_id is not None:
        data["goal_id"] = goal_id
    if knowledge_base_id is not None:
        data["knowledge_base_id"] = knowledge_base_id
    return RetrievalFilter(**data) if data else None
