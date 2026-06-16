from __future__ import annotations

from datetime import date as DateType, datetime
from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, Field, model_validator


TaskStatus = Literal["pending", "scheduled", "in_progress", "completed", "delayed", "cancelled", "archived"]
TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskSourceType = Literal["manual", "ai_optimized", "ai_supplement", "imported", "planner"]
TaskSessionStatus = Literal["running", "paused", "completed"]


class TaskItemCreate(BaseModel):
    content: str = Field(validation_alias=AliasChoices("content", "title"), min_length=1)
    goal_id: int | None = None
    domain: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=128)
    task_type: str | None = Field(default=None, max_length=64)
    planned_date: DateType | None = Field(default=None, validation_alias=AliasChoices("planned_date", "date"))
    status: TaskStatus = "pending"
    priority: TaskPriority = "medium"
    estimated_minutes: int = Field(default=60, ge=5, le=10000)
    source_type: TaskSourceType = "manual"
    ai_reason: str | None = None
    context_json: dict[str, Any] | list[Any] | None = None

    model_config = {"populate_by_name": True}


class TaskItemUpdate(BaseModel):
    content: str | None = Field(default=None, validation_alias=AliasChoices("content", "title"), min_length=1)
    goal_id: int | None = None
    domain: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=128)
    task_type: str | None = Field(default=None, max_length=64)
    planned_date: DateType | None = Field(default=None, validation_alias=AliasChoices("planned_date", "date"))
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    estimated_minutes: int | None = Field(default=None, ge=5, le=10000)
    actual_minutes: int | None = Field(default=None, ge=0, le=10000)
    source_type: TaskSourceType | None = None
    ai_reason: str | None = None
    context_json: dict[str, Any] | list[Any] | None = None

    model_config = {"populate_by_name": True}


class TaskItemOut(BaseModel):
    id: int
    user_id: int
    goal_id: int | None = None
    content: str
    domain: str | None = None
    category: str | None = None
    task_type: str | None = None
    planned_date: DateType | None = None
    status: str
    priority: str
    estimated_minutes: int
    actual_minutes: int | None = None
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None
    source_type: str
    ai_reason: str | None = None
    context_json: dict[str, Any] | list[Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskCompleteRequest(BaseModel):
    actual_minutes: int | None = Field(default=None, ge=0, le=10000)


class TaskExecutionSessionOut(BaseModel):
    id: int
    user_id: int
    task_id: int
    started_at: datetime
    ended_at: datetime | None = None
    duration_minutes: int | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskOptimizeRequest(BaseModel):
    raw_content: str | None = Field(default=None, max_length=2000)
    raw_title: str | None = Field(default=None, max_length=2000)
    raw_description: str | None = None
    date: DateType | None = None
    category: str | None = Field(default=None, max_length=128)
    estimated_minutes: int | None = Field(default=None, ge=5, le=10000)
    priority: TaskPriority = "medium"
    context: dict[str, Any] | str | None = None

    @model_validator(mode="after")
    def require_content(self):
        if not (self.raw_content or self.raw_title):
            raise ValueError("raw_content is required")
        return self


class TaskOptimizeResponse(BaseModel):
    suggested_content: str
    suggested_category: str | None = None
    suggested_estimated_minutes: int
    suggested_priority: TaskPriority
    reason: str
    warnings: list[str] = Field(default_factory=list)


class TaskSupplementRequest(BaseModel):
    planned_date: DateType = Field(validation_alias=AliasChoices("planned_date", "date"))
    goal_id: int | None = None
    available_minutes: int = Field(ge=15, le=1440)
    max_new_tasks: int = Field(default=3, ge=1, le=5)
    preferences: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class TaskSuggestion(BaseModel):
    content: str
    category: str | None = None
    task_type: str | None = None
    estimated_minutes: int
    priority: TaskPriority
    reason: str
    source_type: Literal["ai_supplement"] = "ai_supplement"
    confidence: float | None = None
    risk_level: Literal["low", "medium", "high"] | None = None


class TaskSupplementResponse(BaseModel):
    suggestions: list[TaskSuggestion]
    message: str


class CalendarDaySummary(BaseModel):
    date: DateType
    task_count: int = 0
    completed_count: int = 0
    unfinished_count: int = 0
    estimated_minutes: int = 0
    actual_minutes: int = 0
    completion_rate: int = 0
    has_delayed: bool = False
    titles: list[str] = Field(default_factory=list)


class CalendarMonthSummaryResponse(BaseModel):
    year: int
    month: int
    days: list[CalendarDaySummary]
