from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.planner_service import PlannerService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/today")
def today_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PlannerService(db).today_tasks(current_user.id)


@router.put("/{task_id}/complete")
def complete_task(task_id: int, current_user: User = Depends(get_current_user)):
    return {"task_id": task_id, "status": "completed"}
