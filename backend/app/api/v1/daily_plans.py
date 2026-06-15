from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.planner.daily_plan_service import DailyPlanService
from app.planner.task_schemas import (
    DailyPlanAdjustRequest,
    DailyPlanAdjustResponse,
    DailyPlanGenerateRequest,
    DailyPlanGenerateResponse,
    DailyPlanRead,
    DailyPlanTaskRead,
    DailyPlanTaskStatusUpdate,
    DailyPlanTaskFeedbackCreate,
    DailyPlanTaskFeedbackRead,
)

router = APIRouter(prefix="/daily-plans", tags=["daily-plans"])


@router.post("/generate", response_model=DailyPlanGenerateResponse)
def generate_daily_plan(
    payload: DailyPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DailyPlanService(db).generate(current_user.id, payload)


@router.post("/adjust", response_model=DailyPlanAdjustResponse)
def adjust_daily_plans(
    payload: DailyPlanAdjustRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DailyPlanService(db).adjust(current_user.id, payload)


@router.get("/today", response_model=DailyPlanRead | None)
def get_today_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DailyPlanService(db).today(current_user.id)


@router.get("", response_model=DailyPlanRead | None)
def get_plan_by_date(
    plan_date: date = Query(alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DailyPlanService(db).by_date(current_user.id, plan_date)


@router.post("/{daily_plan_id}/confirm", response_model=DailyPlanRead)
def confirm_daily_plan(
    daily_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DailyPlanService(db).confirm(current_user.id, daily_plan_id)


@router.patch("/{daily_plan_id}/tasks/{daily_plan_task_id}/status", response_model=DailyPlanTaskRead)
def update_daily_plan_task_status(
    daily_plan_id: int,
    daily_plan_task_id: int,
    payload: DailyPlanTaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DailyPlanService(db).update_task_status(
        current_user.id,
        daily_plan_id,
        daily_plan_task_id,
        payload,
    )


@router.post("/{daily_plan_id}/tasks/{daily_plan_task_id}/feedback", response_model=DailyPlanTaskFeedbackRead)
def create_daily_plan_task_feedback(
    daily_plan_id: int,
    daily_plan_task_id: int,
    payload: DailyPlanTaskFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DailyPlanService(db).create_feedback(
        current_user.id,
        daily_plan_id,
        daily_plan_task_id,
        payload,
    )
