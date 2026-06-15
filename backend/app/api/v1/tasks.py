from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.planner.task_schemas import (
    RagTaskRecommendationRequest,
    RagTaskRecommendationResponse,
    TaskItemBulkCreateRequest,
    TaskItemBulkCreateResponse,
    TaskItemCreate,
    TaskItemRead,
    TaskItemUpdate,
    TaskOrganizeRequest,
    TaskOrganizeResponse,
    TaskSplitResponse,
)
from app.planner.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskItemRead)
def create_task(
    payload: TaskItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).create_task(current_user.id, payload)


@router.post("/bulk", response_model=TaskItemBulkCreateResponse)
def bulk_create_tasks(
    payload: TaskItemBulkCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).bulk_create(current_user.id, payload)


@router.get("", response_model=list[TaskItemRead])
def list_tasks(
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    subject: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    deadline_before: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).list_tasks(
        current_user.id,
        status_filter=status,
        category=category,
        subject=subject,
        priority=priority,
        deadline_before=deadline_before,
    )


@router.post("/ai/organize", response_model=TaskOrganizeResponse)
def organize_tasks(
    payload: TaskOrganizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).organize_tasks(current_user.id, payload)


@router.post("/ai/recommend-from-rag", response_model=RagTaskRecommendationResponse)
def recommend_tasks_from_rag(
    payload: RagTaskRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).recommend_from_rag(current_user.id, payload)


@router.patch("/{task_id}", response_model=TaskItemRead)
def update_task(
    task_id: int,
    payload: TaskItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).update_task(current_user.id, task_id, payload)


@router.delete("/{task_id}", response_model=TaskItemRead)
def archive_task_by_delete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).archive_task(current_user.id, task_id)


@router.patch("/{task_id}/archive", response_model=TaskItemRead)
def archive_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).archive_task(current_user.id, task_id)


@router.post("/{task_id}/split", response_model=TaskSplitResponse)
def split_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaskService(db).split_task(current_user.id, task_id)
