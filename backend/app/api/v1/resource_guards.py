from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.document import Document
from app.models.goal import Goal
from app.models.knowledge_base import KnowledgeBase


def get_owned_goal(db: Session, user_id: int, goal_id: int) -> Goal:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        raise NotFoundError("Goal not found")
    return goal


def get_owned_knowledge_base(db: Session, user_id: int, kb_id: int) -> KnowledgeBase:
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user_id).first()
    if not kb:
        raise NotFoundError("Knowledge base not found")
    return kb


def get_owned_document(db: Session, user_id: int, document_id: int) -> Document:
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()
    if not document:
        raise NotFoundError("Document not found")
    return document


def validate_goal_id(db: Session, user_id: int, goal_id: int | None) -> int | None:
    if goal_id is None:
        return None
    return get_owned_goal(db, user_id, goal_id).id


def validate_knowledge_base_id(db: Session, user_id: int, kb_id: int | None) -> int | None:
    if kb_id is None:
        return None
    return get_owned_knowledge_base(db, user_id, kb_id).id


def validate_learning_context(
    db: Session,
    user_id: int,
    *,
    goal_id: int | None = None,
    knowledge_base_id: int | None = None,
) -> tuple[int | None, int | None]:
    normalized_goal_id = validate_goal_id(db, user_id, goal_id)
    normalized_kb_id = validate_knowledge_base_id(db, user_id, knowledge_base_id)

    if normalized_kb_id is None:
        return normalized_goal_id, None

    kb = get_owned_knowledge_base(db, user_id, normalized_kb_id)
    if kb.goal_id is None:
        return normalized_goal_id, normalized_kb_id

    if normalized_goal_id is None:
        return kb.goal_id, normalized_kb_id

    if kb.goal_id != normalized_goal_id:
        raise BadRequestError("Knowledge base is bound to a different goal")
    return normalized_goal_id, normalized_kb_id
