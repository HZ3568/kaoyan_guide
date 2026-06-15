import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import BadRequestError
from app.models.user import User
from app.schemas.document import ChunkRead, DocumentRead, LocalImportRequest, LocalImportResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    source: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    subject: str | None = Form(default=None),
    school: str | None = Form(default=None),
    major: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    exam_year: int | None = Form(default=None),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await DocumentService(db).upload_and_parse(
        file,
        user_id=current_user.id,
        title=title,
        source=source,
        source_url=source_url,
        subject=subject,
        school=school,
        major=major,
        tags=_parse_tags(tags),
        exam_year=exam_year,
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
        title=payload.title,
        source=payload.source,
        source_url=payload.source_url,
        subject=payload.subject,
        school=payload.school,
        major=payload.major,
        tags=payload.tags,
        exam_year=payload.exam_year,
        description=payload.description,
    )
    return LocalImportResponse(imported=result.imported, errors=result.errors)


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return DocumentService(db).list_documents(user_id=current_user.id)


@router.get("/{document_id}/chunks", response_model=list[ChunkRead])
def list_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).list_chunks(document_id, user_id=current_user.id)


@router.post("/{document_id}/embed")
def embed_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    DocumentService(db).get_document(document_id, user_id=current_user.id)
    return {"document_id": document_id, "status": "embedding placeholder"}


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
