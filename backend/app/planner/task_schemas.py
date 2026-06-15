from __future__ import annotations

from datetime import date as DateType, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


TaskItemStatus = Literal[
    "pending",
    "scheduled",
    "in_progress",
    "completed",
    "delayed",
    "skipped",
    "overdue",
    "cancelled",
    "archived",
]
TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskDifficulty = Literal["easy", "normal", "hard", "very_hard"]
TaskSourceType = Literal["manual", "ai_optimized", "ai_supplement", "ai_split", "imported", "planner"]
DailyPlanStatus = Literal["suggested", "confirmed", "finished"]
DailyPlanCreatedBy = Literal["user", "ai"]
DailyPlanTaskStatus = Literal[
    "suggested",
    "accepted",
    "pending",
    "in_progress",
    "completed",
    "delayed",
    "skipped",
    "removed",
]
SuggestionType = Literal[
    "estimate_time",
    "split",
    "adjust_priority",
    "optimize",
    "supplement",
    "today_plan",
    "reschedule",
    "summarize",
]


class TaskItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=64)
    subject: str | None = Field(default=None, max_length=64)
    project: str | None = Field(default=None, max_length=128)
    priority: TaskPriority = "medium"
    difficulty: TaskDifficulty | None = "normal"
    estimated_minutes: int = Field(default=60, ge=5, le=10000)
    deadline: DateType | None = None
    status: TaskItemStatus = "pending"
    parent_task_id: int | None = None
    is_splittable: bool = True
    is_ai_generated: bool = False
    source_type: TaskSourceType = "manual"
    source_ref: dict[str, Any] | list[Any] | str | None = None
    task_date: DateType | None = Field(default=None, alias="date")

    model_config = {"populate_by_name": True}


class TaskItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=64)
    subject: str | None = Field(default=None, max_length=64)
    project: str | None = Field(default=None, max_length=128)
    priority: TaskPriority | None = None
    difficulty: TaskDifficulty | None = None
    estimated_minutes: int | None = Field(default=None, ge=5, le=10000)
    deadline: DateType | None = None
    status: TaskItemStatus | None = None
    parent_task_id: int | None = None
    is_splittable: bool | None = None
    source_type: TaskSourceType | None = None
    source_ref: dict[str, Any] | list[Any] | str | None = None
    task_date: DateType | None = Field(default=None, alias="date")

    model_config = {"populate_by_name": True}


class TaskItemRead(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None = None
    category: str | None = None
    subject: str | None = None
    project: str | None = None
    priority: str
    difficulty: str | None = None
    estimated_minutes: int
    deadline: DateType | None = None
    status: str
    parent_task_id: int | None = None
    is_splittable: bool
    is_ai_generated: bool
    source_type: str
    source_ref: dict[str, Any] | list[Any] | str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskAiSuggestionRead(BaseModel):
    id: int
    user_id: int
    task_id: int | None = None
    suggestion_type: str
    suggestion_content: dict[str, Any] | list[Any] | str
    accepted: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskSplitResponse(BaseModel):
    task: TaskItemRead
    suggestions: list[TaskAiSuggestionRead]
    message: str


class TaskOrganizeRequest(BaseModel):
    status: list[TaskItemStatus] | None = None
    limit: int = Field(default=50, ge=1, le=200)


class TaskOrganizeResponse(BaseModel):
    suggestions: list[TaskAiSuggestionRead]
    message: str


class TaskStatusUpdate(BaseModel):
    status: TaskItemStatus


class TaskFeedbackCreate(BaseModel):
    actual_minutes: int | None = Field(default=None, ge=0, le=1440)
    difficulty_feedback: TaskDifficulty | None = None
    completion_note: str | None = None


class TaskOptimizeRequest(BaseModel):
    raw_title: str = Field(min_length=1, max_length=255)
    raw_description: str | None = None
    date: DateType | None = None
    subject: str | None = Field(default=None, max_length=64)
    estimated_minutes: int | None = Field(default=None, ge=5, le=10000)
    priority: TaskPriority = "medium"
    context: dict[str, Any] | str | None = None


class TaskOptimizeResponse(BaseModel):
    suggested_title: str
    suggested_description: str | None = None
    suggested_subject: str | None = None
    suggested_estimated_minutes: int
    suggested_priority: TaskPriority
    reason: str
    warnings: list[str] = Field(default_factory=list)


class DailyPlanPreferences(BaseModel):
    max_tasks: int = Field(default=5, ge=1, le=20)
    prefer_mixed_categories: bool = True
    include_overdue: bool = True


class DailyPlanGenerateRequest(BaseModel):
    plan_date: DateType = Field(alias="date")
    available_minutes: int = Field(ge=15, le=1440)
    preferences: DailyPlanPreferences = Field(default_factory=DailyPlanPreferences)

    model_config = {"populate_by_name": True}


class DailyPlanTaskRead(BaseModel):
    id: int
    daily_plan_id: int
    task_id: int
    order_index: int
    planned_minutes: int
    planned_start_time: time | None = None
    planned_end_time: time | None = None
    reason: str | None = None
    status: str
    task: TaskItemRead | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DailyPlanRead(BaseModel):
    id: int
    user_id: int
    plan_date: DateType
    available_minutes: int
    summary: str | None = None
    status: str
    created_by: str
    tasks: list[DailyPlanTaskRead] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DailyPlanGenerateResponse(BaseModel):
    daily_plan_id: int
    status: str
    suggested_tasks: list[DailyPlanTaskRead]
    total_planned_minutes: int
    reason: str


class DailyPlanTaskStatusUpdate(BaseModel):
    status: DailyPlanTaskStatus


class DailyPlanTaskFeedbackCreate(BaseModel):
    actual_minutes: int | None = Field(default=None, ge=0, le=1440)
    difficulty_feedback: TaskDifficulty | None = None
    completion_note: str | None = None


class DailyPlanTaskFeedbackRead(BaseModel):
    id: int
    task_id: int
    daily_plan_task_id: int | None = None
    user_id: int
    actual_minutes: int | None = None
    difficulty_feedback: str | None = None
    completion_note: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class DailyPlanAdjustRequest(BaseModel):
    from_date: DateType | None = None
    days: int = Field(default=7, ge=1, le=30)


class DailyPlanAdjustResponse(BaseModel):
    adjusted_task_ids: list[int] = Field(default_factory=list)
    suggestion_ids: list[int] = Field(default_factory=list)
    message: str


class CalendarDaySummary(BaseModel):
    date: DateType
    task_count: int = 0
    completed_count: int = 0
    unfinished_count: int = 0
    estimated_minutes: int = 0
    completion_rate: int = 0
    has_delayed: bool = False
    titles: list[str] = Field(default_factory=list)


class CalendarMonthSummaryResponse(BaseModel):
    year: int
    month: int
    days: list[CalendarDaySummary]


class CalendarTaskSupplementPreferences(BaseModel):
    prefer_mixed_categories: bool = True
    include_delayed: bool = True


class CalendarTaskSupplementRequest(BaseModel):
    plan_date: DateType = Field(alias="date")
    available_minutes: int = Field(ge=15, le=1440)
    max_new_tasks: int = Field(default=3, ge=1, le=5)
    preferences: CalendarTaskSupplementPreferences = Field(default_factory=CalendarTaskSupplementPreferences)

    model_config = {"populate_by_name": True}


class CalendarTaskSuggestion(BaseModel):
    title: str
    description: str | None = None
    category: str | None = None
    subject: str | None = None
    estimated_minutes: int
    priority: TaskPriority
    reason: str
    source_type: Literal["ai_supplement"] = "ai_supplement"
    confidence: float | None = None
    risk_level: Literal["low", "medium", "high"] | None = None


class CalendarTaskSupplementResponse(BaseModel):
    suggestions: list[CalendarTaskSuggestion]
    message: str


class TaskItemBulkCreateRequest(BaseModel):
    tasks: list[TaskItemCreate] = Field(min_length=1, max_length=50)


class TaskItemBulkCreateResponse(BaseModel):
    tasks: list[TaskItemRead]


class TaskMoveRequest(BaseModel):
    parent_task_id: int | None = None

    @model_validator(mode="after")
    def validate_parent(self):
        return self
