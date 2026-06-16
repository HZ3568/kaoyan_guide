from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.planner.task_schemas import (
    CalendarMonthSummaryResponse,
    TaskCompleteRequest,
    TaskExecutionSessionOut,
    TaskItemCreate,
    TaskItemOut,
    TaskItemUpdate,
    TaskOptimizeRequest,
    TaskOptimizeResponse,
    TaskStatusUpdate,
    TaskSupplementRequest,
    TaskSupplementResponse,
)
from app.planner.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskItemOut)
def create_task(
    payload: TaskItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).create_task(current_user.id, payload)


@router.get("", response_model=list[TaskItemOut])
def list_tasks(
    goal_id: int | None = Query(default=None),
    planned_date: date | None = Query(default=None, alias="date"),
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).list_tasks(
        current_user.id,
        goal_id=goal_id,
        planned_date=planned_date,
        status_filter=status,
        category=category,
    )


@router.get("/month", response_model=CalendarMonthSummaryResponse)
def task_month_summary(
    year: int = Query(ge=1970, le=2100),
    month: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).month_summary(current_user.id, year=year, month=month)


@router.post("/ai/optimize", response_model=TaskOptimizeResponse)
def optimize_task(
    payload: TaskOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).optimize_task(current_user.id, payload)


@router.post("/ai/supplement", response_model=TaskSupplementResponse)
def supplement_tasks(
    payload: TaskSupplementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).supplement_tasks(current_user.id, payload)


@router.get("/{task_id}", response_model=TaskItemOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService(db).get_task(current_user.id, task_id)


@router.patch("/{task_id}", response_model=TaskItemOut)
def update_task(
    task_id: int,
    payload: TaskItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).update_task(current_user.id, task_id, payload)


@router.delete("/{task_id}", response_model=TaskItemOut)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService(db).delete_task(current_user.id, task_id)


@router.patch("/{task_id}/status", response_model=TaskItemOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).update_status(current_user.id, task_id, payload.status)


@router.post("/{task_id}/postpone", response_model=TaskItemOut)
def postpone_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService(db).postpone_task(current_user.id, task_id)


@router.post("/{task_id}/start", response_model=TaskExecutionSessionOut)
def start_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService(db).start_task(current_user.id, task_id)


@router.post("/{task_id}/pause", response_model=TaskExecutionSessionOut)
def pause_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService(db).pause_task(current_user.id, task_id)


@router.post("/{task_id}/complete", response_model=TaskItemOut)
def complete_task(
    task_id: int,
    payload: TaskCompleteRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).complete_task(current_user.id, task_id, payload)
