from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.api.v1.resource_guards import get_owned_goal
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.rag_log import RagQueryLog
from app.models.user import User
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseOut, KnowledgeBaseUpdate

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


@router.get("", response_model=list[KnowledgeBaseOut])
def list_knowledge_bases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.user_id == current_user.id)
        .order_by(KnowledgeBase.created_at.desc())
        .all()
    )


@router.post("", response_model=KnowledgeBaseOut)
def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.goal_id is not None:
        get_owned_goal(db, current_user.id, payload.goal_id)
    kb = KnowledgeBase(user_id=current_user.id, **payload.model_dump())
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


@router.get("/{kb_id}", response_model=KnowledgeBaseOut)
def get_knowledge_base(kb_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_kb(db, current_user.id, kb_id)


@router.patch("/{kb_id}", response_model=KnowledgeBaseOut)
def update_knowledge_base(
    kb_id: int,
    payload: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = _get_kb(db, current_user.id, kb_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("goal_id") is not None:
        get_owned_goal(db, current_user.id, data["goal_id"])
    for key, value in data.items():
        setattr(kb, key, value)
    db.commit()
    db.refresh(kb)
    return kb


@router.delete("/{kb_id}", response_model=KnowledgeBaseOut)
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kb = _get_kb(db, current_user.id, kb_id)
    db.query(DocumentChunk).filter(DocumentChunk.user_id == current_user.id, DocumentChunk.knowledge_base_id == kb.id).delete(
        synchronize_session=False
    )
    db.query(Document).filter(Document.user_id == current_user.id, Document.knowledge_base_id == kb.id).delete(
        synchronize_session=False
    )
    db.query(RagQueryLog).filter(RagQueryLog.user_id == current_user.id, RagQueryLog.knowledge_base_id == kb.id).delete(
        synchronize_session=False
    )
    db.delete(kb)
    db.commit()
    return kb


@router.post("/{kb_id}/bind-goal/{goal_id}", response_model=KnowledgeBaseOut)
def bind_goal(
    kb_id: int,
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = _get_kb(db, current_user.id, kb_id)
    get_owned_goal(db, current_user.id, goal_id)
    kb.goal_id = goal_id
    db.commit()
    db.refresh(kb)
    return kb


def _get_kb(db: Session, user_id: int, kb_id: int) -> KnowledgeBase:
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user_id).first()
    if not kb:
        raise NotFoundError("Knowledge base not found")
    return kb
