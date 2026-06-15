from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


TaskItemStatus = Literal["backlog", "pending", "in_progress", "completed", "delayed", "skipped", "archived"]
TaskPriority = Literal["low", "medium", "high", "urgent"]
TaskDifficulty = Literal["easy", "normal", "hard", "very_hard"]
TaskSourceType = Literal["manual", "ai_split", "rag_recommendation", "imported", "planner"]
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
    "split_task",
    "adjust_priority",
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
    deadline: date | None = None
    status: TaskItemStatus = "backlog"
    parent_task_id: int | None = None
    is_splittable: bool = True
    is_ai_generated: bool = False
    source_type: TaskSourceType = "manual"
    source_ref: dict[str, Any] | list[Any] | str | None = None


class TaskItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=64)
    subject: str | None = Field(default=None, max_length=64)
    project: str | None = Field(default=None, max_length=128)
    priority: TaskPriority | None = None
    difficulty: TaskDifficulty | None = None
    estimated_minutes: int | None = Field(default=None, ge=5, le=10000)
    deadline: date | None = None
    status: TaskItemStatus | None = None
    parent_task_id: int | None = None
    is_splittable: bool | None = None
    source_type: TaskSourceType | None = None
    source_ref: dict[str, Any] | list[Any] | str | None = None


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
    deadline: date | None = None
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


class DailyPlanPreferences(BaseModel):
    max_tasks: int = Field(default=5, ge=1, le=20)
    prefer_mixed_categories: bool = True
    include_overdue: bool = True


class DailyPlanGenerateRequest(BaseModel):
    plan_date: date = Field(alias="date")
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
    plan_date: date
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
    from_date: date | None = None
    days: int = Field(default=7, ge=1, le=30)


class DailyPlanAdjustResponse(BaseModel):
    adjusted_task_ids: list[int] = Field(default_factory=list)
    suggestion_ids: list[int] = Field(default_factory=list)
    message: str


class RagTaskRecommendationRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=10)
    max_tasks: int = Field(default=5, ge=1, le=10)


class RagTaskRecommendationResponse(BaseModel):
    suggestions: list[TaskAiSuggestionRead]
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
