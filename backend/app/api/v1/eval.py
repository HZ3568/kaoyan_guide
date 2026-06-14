from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/eval", tags=["eval"])


@router.get("/rag-records")
def rag_eval_records(current_user: User = Depends(get_current_user)):
    return {"records": [], "message": "RAG evaluation placeholder"}
