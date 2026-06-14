from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.rag import ChatRequest, ChatResponse, RetrieveRequest, RetrievedChunk
from app.services.rag_service import RagService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/rag", tags=["rag"])


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
