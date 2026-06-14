from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.planner import GeneratePlanRequest, LearningPlanRead, LearningProfileCreate, LearningProfileRead
from app.services.planner_service import PlannerService

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/profiles", response_model=LearningProfileRead)
def create_profile(
    payload: LearningProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PlannerService(db).create_profile(current_user.id, payload)


@router.post("/generate", response_model=LearningPlanRead)
def generate_plan(
    payload: GeneratePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PlannerService(db).generate_plan(current_user.id, payload)


@router.get("/plans", response_model=list[LearningPlanRead])
def list_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PlannerService(db).list_plans(current_user.id)
