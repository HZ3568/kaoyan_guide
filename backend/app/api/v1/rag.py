from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.rag.vector_store import VectorStoreError
from app.schemas.rag import (
    RagAskRequest,
    RagAskResponse,
    ChatRequest,
    ChatResponse,
    RagSearchRequest,
    RagSearchResult,
    RetrieveRequest,
    RetrievedChunk,
    VectorIndexRequest,
    VectorIndexResponse,
    VectorIndexStatus,
)
from app.llm.client import LLMError
from app.services.embedding_service import EmbeddingError
from app.services.rag_service import RagService
from app.services.retrieval_service import RetrievalService
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
            limit=payload.limit,
            batch_size=payload.batch_size,
            force_reindex=payload.force_reindex,
        )
    except (EmbeddingError, VectorStoreError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return VectorIndexResponse(
        indexed=result.indexed,
        skipped=result.skipped,
        failed=result.failed,
        errors=result.errors,
        index_name=result.index_name,
        embedding_dim=result.embedding_dim,
    )


@router.get("/index/status", response_model=VectorIndexStatus)
def index_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return VectorIndexService(db).status(user_id=current_user.id)
    except VectorStoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/search", response_model=list[RagSearchResult])
def search(
    payload: RagSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        results = VectorIndexService(db).search(
            query=payload.query,
            top_k=payload.top_k,
            user_id=current_user.id,
            filters=payload.filters,
        )
    except (EmbeddingError, VectorStoreError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return [
        RagSearchResult(
            chunk_id=item.chunk_id,
            document_id=item.document_id,
            score=item.score,
            content=item.content,
            source=item.source,
            page_number=item.page_number,
            location=item.location,
            metadata=item.metadata,
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
            session_id=payload.session_id,
            stream=payload.stream,
        )
    except (EmbeddingError, VectorStoreError, LLMError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/retrieve", response_model=list[RetrievedChunk])
def retrieve(
    payload: RetrieveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RetrievalService(db).retrieve(
        payload.query,
        top_k=payload.top_k,
        user_id=current_user.id,
        filters=payload.filters,
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RagService(db).chat(payload.question, user_id=current_user.id, filters=payload.filters)


@router.get("/sessions")
def sessions(current_user: User = Depends(get_current_user)):
    return []
