from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class DailyReviewCreate(BaseModel):
    goal_id: int | None = None
    review_date: date
    completion_rate: int = Field(default=0, ge=0, le=100)
    total_estimated_minutes: int = Field(default=0, ge=0)
    total_actual_minutes: int = Field(default=0, ge=0)
    summary: str | None = None
    problems: str | None = None
    adjustment_suggestion: str | None = None
    metadata_json: dict[str, Any] | list[Any] | None = None


class DailyReviewUpdate(BaseModel):
    completion_rate: int | None = Field(default=None, ge=0, le=100)
    total_estimated_minutes: int | None = Field(default=None, ge=0)
    total_actual_minutes: int | None = Field(default=None, ge=0)
    summary: str | None = None
    problems: str | None = None
    adjustment_suggestion: str | None = None
    metadata_json: dict[str, Any] | list[Any] | None = None


class DailyReviewOut(DailyReviewCreate):
    id: int
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ReviewStatsOut(BaseModel):
    goal_id: int | None = None
    total_tasks: int
    completed_tasks: int
    delayed_tasks: int
    completion_rate: int
    delay_rate: int
    estimated_minutes: int
    actual_minutes: int
    actual_estimated_delta_minutes: int
