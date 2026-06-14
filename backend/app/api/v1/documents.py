from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.document import ChunkRead, DocumentRead
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await DocumentService(db).upload_and_parse(file, user_id=current_user.id)


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
