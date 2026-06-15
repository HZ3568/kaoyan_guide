from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.planner.calendar_task_service import CalendarTaskService
from app.planner.task_schemas import (
    CalendarMonthSummaryResponse,
    CalendarTaskSupplementRequest,
    CalendarTaskSupplementResponse,
    DailyPlanRead,
    TaskItemCreate,
    TaskItemRead,
)
from app.planner.task_service import TaskService

router = APIRouter(prefix="/calendar-tasks", tags=["calendar-tasks"])


@router.get("/month", response_model=CalendarMonthSummaryResponse)
def get_month_summary(
    year: int = Query(ge=1970, le=2100),
    month: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarTaskService(db).month_summary(current_user.id, year=year, month=month)


@router.get("", response_model=DailyPlanRead | None)
def get_calendar_tasks_by_date(
    plan_date: date = Query(alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarTaskService(db).by_date(current_user.id, plan_date)


@router.post("/ai/supplement", response_model=CalendarTaskSupplementResponse)
def supplement_calendar_tasks(
    payload: CalendarTaskSupplementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarTaskService(db).supplement(current_user.id, payload)


@router.post("/accept-suggestion", response_model=TaskItemRead)
def accept_calendar_task_suggestion(
    payload: TaskItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).create_task(current_user.id, payload)
