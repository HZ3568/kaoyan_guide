from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.planner.ai_task_assistant import AiTaskAssistant
from app.planner.task_models import DailyPlan, DailyPlanTask, TaskAiSuggestion, TaskFeedback, TaskItem
from app.planner.task_schemas import (
    TaskAiSuggestionRead,
    TaskFeedbackCreate,
    TaskItemBulkCreateRequest,
    TaskItemBulkCreateResponse,
    TaskItemCreate,
    TaskItemRead,
    TaskItemUpdate,
    TaskOptimizeRequest,
    TaskOptimizeResponse,
    TaskOrganizeRequest,
    TaskOrganizeResponse,
    TaskSplitResponse,
    TaskStatusUpdate,
)


class TaskService:
    def __init__(self, db: Session, *, ai_assistant: AiTaskAssistant | None = None) -> None:
        self.db = db
        self.ai_assistant = ai_assistant or AiTaskAssistant()

    def create_task(self, user_id: int, payload: TaskItemCreate) -> TaskItemRead:
        task_date = payload.task_date
        data = payload.model_dump(exclude={"task_date"})
        task = TaskItem(user_id=user_id, **data)
        self.db.add(task)
        self.db.flush()
        if task_date:
            self._schedule_task_on_date(user_id, task, task_date)
        self.db.commit()
        self.db.refresh(task)
        return TaskItemRead.model_validate(task)

    def bulk_create(self, user_id: int, payload: TaskItemBulkCreateRequest) -> TaskItemBulkCreateResponse:
        tasks: list[TaskItem] = []
        for item in payload.tasks:
            task_date = item.task_date
            task = TaskItem(user_id=user_id, **item.model_dump(exclude={"task_date"}))
            self.db.add(task)
            self.db.flush()
            if task_date:
                self._schedule_task_on_date(user_id, task, task_date)
            tasks.append(task)
        self.db.commit()
        for task in tasks:
            self.db.refresh(task)
        return TaskItemBulkCreateResponse(tasks=[TaskItemRead.model_validate(task) for task in tasks])

    def list_tasks(
        self,
        user_id: int,
        *,
        status_filter: str | None = None,
        category: str | None = None,
        subject: str | None = None,
        priority: str | None = None,
        deadline_before: date | None = None,
        task_date: date | None = None,
    ) -> list[TaskItemRead]:
        if task_date:
            query = (
                self.db.query(TaskItem)
                .join(DailyPlanTask, DailyPlanTask.task_id == TaskItem.id)
                .join(DailyPlan, DailyPlan.id == DailyPlanTask.daily_plan_id)
                .filter(DailyPlan.user_id == user_id, DailyPlan.plan_date == task_date)
                .filter(DailyPlanTask.status != "removed")
            )
        else:
            query = self.db.query(TaskItem).filter(TaskItem.user_id == user_id)
        if status_filter:
            query = query.filter(TaskItem.status == self._normalize_status(status_filter))
        if category:
            query = query.filter(TaskItem.category == category)
        if subject:
            query = query.filter(TaskItem.subject == subject)
        if priority:
            query = query.filter(TaskItem.priority == priority)
        if deadline_before:
            query = query.filter(TaskItem.deadline <= deadline_before)
        tasks = query.order_by(TaskItem.status.asc(), TaskItem.deadline.asc(), TaskItem.id.desc()).all()
        return [TaskItemRead.model_validate(task) for task in tasks]

    def update_task(self, user_id: int, task_id: int, payload: TaskItemUpdate) -> TaskItemRead:
        task = self._get_task(user_id, task_id)
        data = payload.model_dump(exclude_unset=True, exclude={"task_date"})
        if "parent_task_id" in data and data["parent_task_id"] == task.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task cannot be its own parent")
        if "status" in data and data["status"]:
            data["status"] = self._normalize_status(data["status"])
        for key, value in data.items():
            setattr(task, key, value)
        if payload.task_date:
            self._schedule_task_on_date(user_id, task, payload.task_date)
        self.db.commit()
        self.db.refresh(task)
        return TaskItemRead.model_validate(task)

    def update_status(self, user_id: int, task_id: int, payload: TaskStatusUpdate) -> TaskItemRead:
        task = self._get_task(user_id, task_id)
        task.status = self._normalize_status(payload.status)
        for plan_task in task.daily_plan_tasks:
            if plan_task.status != "removed":
                plan_task.status = self._task_status_to_plan_task_status(task.status)
        self.db.commit()
        self.db.refresh(task)
        return TaskItemRead.model_validate(task)

    def create_feedback(self, user_id: int, task_id: int, payload: TaskFeedbackCreate) -> TaskFeedback:
        task = self._get_task(user_id, task_id)
        feedback = TaskFeedback(
            task_id=task.id,
            daily_plan_task_id=None,
            user_id=user_id,
            actual_minutes=payload.actual_minutes,
            difficulty=payload.difficulty_feedback,
            feedback_text=payload.completion_note,
            difficulty_feedback=payload.difficulty_feedback,
            completion_note=payload.completion_note,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def archive_task(self, user_id: int, task_id: int) -> TaskItemRead:
        task = self._get_task(user_id, task_id)
        task.status = "archived"
        for plan_task in task.daily_plan_tasks:
            if plan_task.status not in {"completed", "removed"}:
                plan_task.status = "removed"
        self.db.commit()
        self.db.refresh(task)
        return TaskItemRead.model_validate(task)

    def optimize_task(self, user_id: int, payload: TaskOptimizeRequest) -> TaskOptimizeResponse:
        result = self.ai_assistant.optimize_task(payload.model_dump())
        suggestion = TaskAiSuggestion(
            user_id=user_id,
            task_id=None,
            suggestion_type="optimize",
            suggestion_content=result,
            accepted=False,
        )
        self.db.add(suggestion)
        self.db.commit()
        return TaskOptimizeResponse.model_validate(result)

    def split_task(self, user_id: int, task_id: int) -> TaskSplitResponse:
        task = self._get_task(user_id, task_id)
        payload = self._task_payload(task)
        split_result = self.ai_assistant.split_task(payload)
        suggestion = TaskAiSuggestion(
            user_id=user_id,
            task_id=task.id,
            suggestion_type="split",
            suggestion_content=split_result,
            accepted=False,
        )
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(task)
        self.db.refresh(suggestion)
        return TaskSplitResponse(
            task=TaskItemRead.model_validate(task),
            suggestions=[TaskAiSuggestionRead.model_validate(suggestion)],
            message="已生成拆分建议，原任务未被覆盖。",
        )

    def organize_tasks(self, user_id: int, payload: TaskOrganizeRequest) -> TaskOrganizeResponse:
        query = self.db.query(TaskItem).filter(TaskItem.user_id == user_id)
        if payload.status:
            query = query.filter(TaskItem.status.in_([self._normalize_status(item) for item in payload.status]))
        tasks = query.order_by(TaskItem.deadline.asc(), TaskItem.priority.desc(), TaskItem.id.asc()).limit(payload.limit).all()
        suggestions_payload = self.ai_assistant.organize_tasks(
            {"tasks": [self._task_payload(task) for task in tasks], "limit": payload.limit}
        )
        suggestions: list[TaskAiSuggestion] = []
        task_ids = {task.id for task in tasks}
        for item in suggestions_payload:
            task_id = item.get("task_id")
            if task_id not in task_ids:
                continue
            suggestion = TaskAiSuggestion(
                user_id=user_id,
                task_id=task_id,
                suggestion_type=item.get("suggestion_type") or "summarize",
                suggestion_content=item.get("content") or {},
                accepted=False,
            )
            self.db.add(suggestion)
            suggestions.append(suggestion)
        self.db.commit()
        for suggestion in suggestions:
            self.db.refresh(suggestion)
        return TaskOrganizeResponse(
            suggestions=[TaskAiSuggestionRead.model_validate(suggestion) for suggestion in suggestions],
            message="已生成任务整理建议，未自动覆盖原任务。",
        )

    def _schedule_task_on_date(self, user_id: int, task: TaskItem, task_date: date) -> DailyPlanTask:
        plan = (
            self.db.query(DailyPlan)
            .options(selectinload(DailyPlan.tasks))
            .filter(DailyPlan.user_id == user_id, DailyPlan.plan_date == task_date)
            .order_by(DailyPlan.created_at.desc(), DailyPlan.id.desc())
            .first()
        )
        if plan is None:
            plan = DailyPlan(
                user_id=user_id,
                plan_date=task_date,
                available_minutes=max(task.estimated_minutes or 0, 0),
                summary="用户手动维护的日期任务安排。",
                status="confirmed",
                created_by="user",
            )
            self.db.add(plan)
            self.db.flush()
        else:
            plan.status = "confirmed" if plan.status == "suggested" else plan.status
            plan.available_minutes = max(plan.available_minutes or 0, task.estimated_minutes or 0)

        existing = (
            self.db.query(DailyPlanTask)
            .filter(DailyPlanTask.daily_plan_id == plan.id, DailyPlanTask.task_id == task.id)
            .first()
        )
        if existing:
            existing.planned_minutes = task.estimated_minutes or existing.planned_minutes
            if existing.status == "removed":
                existing.status = "pending"
            return existing

        order_index = len(plan.tasks or []) + 1
        plan_task = DailyPlanTask(
            daily_plan_id=plan.id,
            task_id=task.id,
            order_index=order_index,
            planned_minutes=task.estimated_minutes or 60,
            reason="用户手动添加到该日期。",
            status=self._task_status_to_plan_task_status(task.status),
        )
        if task.status in {"pending", "scheduled"}:
            task.status = "scheduled"
        self.db.add(plan_task)
        return plan_task

    def _get_task(self, user_id: int, task_id: int) -> TaskItem:
        task = (
            self.db.query(TaskItem)
            .options(selectinload(TaskItem.daily_plan_tasks))
            .filter(TaskItem.id == task_id, TaskItem.user_id == user_id)
            .first()
        )
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    @staticmethod
    def _normalize_status(value: str) -> str:
        return "pending" if value == "back" + "log" else value

    @staticmethod
    def _task_status_to_plan_task_status(value: str) -> str:
        if value == "scheduled":
            return "pending"
        if value == "cancelled":
            return "removed"
        if value in {"pending", "in_progress", "completed", "delayed", "skipped"}:
            return value
        return "pending"

    @staticmethod
    def _task_payload(task: TaskItem) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "category": task.category,
            "subject": task.subject,
            "project": task.project,
            "priority": task.priority,
            "difficulty": task.difficulty,
            "estimated_minutes": task.estimated_minutes,
            "deadline": task.deadline,
            "status": task.status,
            "parent_task_id": task.parent_task_id,
            "is_splittable": task.is_splittable,
            "source_type": task.source_type,
            "source_ref": task.source_ref,
        }
