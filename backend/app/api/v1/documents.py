import json

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import BadRequestError
from app.models.user import User
from app.schemas.document import DocumentChunkOut, DocumentOut, LocalImportRequest, LocalImportResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    knowledge_base_id: int | None = Form(default=None),
    goal_id: int | None = Form(default=None),
    domain: str | None = Form(default=None),
    category: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await DocumentService(db).upload_and_parse(
        file,
        user_id=current_user.id,
        knowledge_base_id=knowledge_base_id,
        goal_id=goal_id,
        domain=domain,
        category=category,
        tags=_parse_tags(tags),
        description=description,
    )


@router.post("/import-local", response_model=LocalImportResponse)
def import_local_documents(
    payload: LocalImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = DocumentService(db).import_local(
        payload.path,
        user_id=current_user.id,
        recursive=payload.recursive,
        knowledge_base_id=payload.knowledge_base_id,
        goal_id=payload.goal_id,
        domain=payload.domain,
        category=payload.category,
        tags=payload.tags,
        description=payload.description,
    )
    return LocalImportResponse(imported=result.imported, errors=result.errors)


@router.get("", response_model=list[DocumentOut])
def list_documents(
    knowledge_base_id: int | None = Query(default=None),
    goal_id: int | None = Query(default=None),
    domain: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).list_documents(
        user_id=current_user.id,
        knowledge_base_id=knowledge_base_id,
        goal_id=goal_id,
        domain=domain,
        category=category,
    )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return DocumentService(db).get_document(document_id, user_id=current_user.id)


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkOut])
def list_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).list_chunks(document_id, user_id=current_user.id)


def _parse_tags(tags: str | None) -> list[str] | None:
    if not tags:
        return None
    text = tags.strip()
    if not text:
        return None
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise BadRequestError("tags must be a JSON array or comma-separated string") from exc
        if not isinstance(parsed, list):
            raise BadRequestError("tags must be a JSON array or comma-separated string")
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [item.strip() for item in text.split(",") if item.strip()]
