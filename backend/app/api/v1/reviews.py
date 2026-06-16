from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.planner.task_models import DailyReview, TaskItem
from app.schemas.review import DailyReviewCreate, DailyReviewOut, DailyReviewUpdate, ReviewStatsOut

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=list[DailyReviewOut])
def list_reviews(
    goal_id: int | None = Query(default=None),
    review_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(DailyReview).filter(DailyReview.user_id == current_user.id)
    if goal_id is not None:
        query = query.filter(DailyReview.goal_id == goal_id)
    if review_date is not None:
        query = query.filter(DailyReview.review_date == review_date)
    return query.order_by(DailyReview.review_date.desc()).all()


@router.post("", response_model=DailyReviewOut)
def create_review(
    payload: DailyReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = DailyReview(user_id=current_user.id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.patch("/{review_id}", response_model=DailyReviewOut)
def update_review(
    review_id: int,
    payload: DailyReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(DailyReview).filter(DailyReview.id == review_id, DailyReview.user_id == current_user.id).first()
    if not review:
        raise NotFoundError("Daily review not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    return review


@router.get("/stats", response_model=ReviewStatsOut)
def review_stats(
    goal_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(TaskItem).filter(TaskItem.user_id == current_user.id)
    if goal_id is not None:
        query = query.filter(TaskItem.goal_id == goal_id)
    tasks = query.all()
    total = len(tasks)
    completed = len([task for task in tasks if task.status == "completed"])
    delayed = len([task for task in tasks if task.status == "delayed"])
    estimated = sum(task.estimated_minutes or 0 for task in tasks)
    actual = sum(task.actual_minutes or 0 for task in tasks)
    return ReviewStatsOut(
        goal_id=goal_id,
        total_tasks=total,
        completed_tasks=completed,
        delayed_tasks=delayed,
        completion_rate=round((completed / total) * 100) if total else 0,
        delay_rate=round((delayed / total) * 100) if total else 0,
        estimated_minutes=estimated,
        actual_minutes=actual,
        actual_estimated_delta_minutes=actual - estimated,
    )
