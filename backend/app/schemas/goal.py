from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


GoalPriority = Literal["low", "medium", "high", "urgent"]
GoalStatus = Literal["active", "paused", "completed", "archived"]


class GoalBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    goal_type: str | None = Field(default=None, max_length=64)
    domain: str | None = Field(default=None, max_length=128)
    target_result: str | None = None
    deadline: date | None = None
    priority: GoalPriority = "medium"
    status: GoalStatus = "active"
    progress: float = Field(default=0, ge=0, le=100)
    context_json: dict[str, Any] | list[Any] | None = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    goal_type: str | None = Field(default=None, max_length=64)
    domain: str | None = Field(default=None, max_length=128)
    target_result: str | None = None
    deadline: date | None = None
    priority: GoalPriority | None = None
    status: GoalStatus | None = None
    progress: float | None = Field(default=None, ge=0, le=100)
    context_json: dict[str, Any] | list[Any] | None = None


class GoalOut(GoalBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
