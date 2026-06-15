from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.planner.ai_task_assistant import AiTaskAssistant
from app.planner.task_adjuster import TaskAdjuster
from app.planner.task_models import DailyPlan, DailyPlanTask, TaskAiSuggestion, TaskFeedback, TaskItem
from app.planner.task_schemas import (
    DailyPlanAdjustRequest,
    DailyPlanAdjustResponse,
    DailyPlanGenerateRequest,
    DailyPlanGenerateResponse,
    DailyPlanRead,
    DailyPlanTaskRead,
    DailyPlanTaskStatusUpdate,
    DailyPlanTaskFeedbackCreate,
    DailyPlanTaskFeedbackRead,
)


PRIORITY_WEIGHT = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
DIFFICULTY_WEIGHT = {"easy": 0, "normal": 1, "hard": 2, "very_hard": 3}


class DailyPlanService:
    def __init__(self, db: Session, *, ai_assistant: AiTaskAssistant | None = None) -> None:
        self.db = db
        self.ai_assistant = ai_assistant or AiTaskAssistant()

    def generate(self, user_id: int, payload: DailyPlanGenerateRequest) -> DailyPlanGenerateResponse:
        candidates = self._candidate_tasks(
            user_id=user_id,
            plan_date=payload.plan_date,
            include_overdue=payload.preferences.include_overdue,
        )
        selected = self._select_tasks(
            candidates,
            plan_date=payload.plan_date,
            available_minutes=payload.available_minutes,
            max_tasks=payload.preferences.max_tasks,
            prefer_mixed_categories=payload.preferences.prefer_mixed_categories,
        )
        explanation = self.ai_assistant.explain_today_plan(
            {
                "date": payload.plan_date,
                "available_minutes": payload.available_minutes,
                "selected_tasks": [self._selected_payload(item) for item in selected],
                "candidate_count": len(candidates),
            }
        )
        daily_plan = DailyPlan(
            user_id=user_id,
            plan_date=payload.plan_date,
            available_minutes=payload.available_minutes,
            summary=explanation.get("summary") or self._summary(selected, payload.available_minutes),
            status="suggested",
            created_by="ai",
        )
        self.db.add(daily_plan)
        self.db.flush()

        reasons = explanation.get("task_reasons") or {}
        plan_tasks: list[DailyPlanTask] = []
        for index, item in enumerate(selected, start=1):
            task = item["task"]
            reason_info = reasons.get(task.id) or reasons.get(str(task.id)) or {}
            reason = reason_info.get("reason") or item["reason"]
            advice = reason_info.get("execution_advice")
            if advice:
                reason = f"{reason}\n执行建议：{advice}"
            plan_task = DailyPlanTask(
                daily_plan_id=daily_plan.id,
                task_id=task.id,
                order_index=index,
                planned_minutes=item["planned_minutes"],
                reason=reason,
                status="suggested",
            )
            self.db.add(plan_task)
            plan_tasks.append(plan_task)

        self._persist_optional_suggestions(user_id, explanation.get("suggestions"))
        self.db.commit()
        self.db.refresh(daily_plan)
        for plan_task in plan_tasks:
            self.db.refresh(plan_task)

        return DailyPlanGenerateResponse(
            daily_plan_id=daily_plan.id,
            status=daily_plan.status,
            suggested_tasks=[DailyPlanTaskRead.model_validate(task) for task in plan_tasks],
            total_planned_minutes=sum(task.planned_minutes for task in plan_tasks),
            reason=daily_plan.summary or "",
        )

    def confirm(self, user_id: int, daily_plan_id: int) -> DailyPlanRead:
        plan = self._get_plan(user_id, daily_plan_id)
        plan.status = "confirmed"
        for plan_task in plan.tasks:
            if plan_task.status == "suggested":
                plan_task.status = "accepted"
            if plan_task.task and plan_task.task.status in {"backlog", "delayed"}:
                plan_task.task.status = "pending"
        self.db.commit()
        return self._read_plan(user_id, daily_plan_id)

    def today(self, user_id: int) -> DailyPlanRead | None:
        return self.by_date(user_id, date.today())

    def by_date(self, user_id: int, plan_date: date) -> DailyPlanRead | None:
        plan = (
            self.db.query(DailyPlan)
            .options(selectinload(DailyPlan.tasks).selectinload(DailyPlanTask.task))
            .filter(DailyPlan.user_id == user_id, DailyPlan.plan_date == plan_date)
            .order_by(DailyPlan.created_at.desc(), DailyPlan.id.desc())
            .first()
        )
        return DailyPlanRead.model_validate(plan) if plan else None

    def update_task_status(
        self,
        user_id: int,
        daily_plan_id: int,
        daily_plan_task_id: int,
        payload: DailyPlanTaskStatusUpdate,
    ) -> DailyPlanTaskRead:
        plan_task = self._get_plan_task(user_id, daily_plan_id, daily_plan_task_id)
        plan_task.status = payload.status
        if plan_task.task:
            if payload.status in {"pending", "in_progress", "completed", "delayed", "skipped"}:
                plan_task.task.status = payload.status
            elif payload.status == "accepted":
                plan_task.task.status = "pending"
        plan = plan_task.daily_plan
        if plan and plan.tasks and all(task.status == "completed" for task in plan.tasks):
            plan.status = "finished"
        self.db.commit()
        self.db.refresh(plan_task)
        return DailyPlanTaskRead.model_validate(plan_task)

    def create_feedback(
        self,
        user_id: int,
        daily_plan_id: int,
        daily_plan_task_id: int,
        payload: DailyPlanTaskFeedbackCreate,
    ) -> DailyPlanTaskFeedbackRead:
        plan_task = self._get_plan_task(user_id, daily_plan_id, daily_plan_task_id)
        feedback = TaskFeedback(
            task_id=plan_task.task_id,
            daily_plan_task_id=plan_task.id,
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
        return DailyPlanTaskFeedbackRead.model_validate(feedback)

    def adjust(self, user_id: int, payload: DailyPlanAdjustRequest) -> DailyPlanAdjustResponse:
        adjusted_task_ids, suggestion_ids = TaskAdjuster(self.db).adjust(
            user_id=user_id,
            from_date=payload.from_date or date.today(),
            days=payload.days,
        )
        self.db.commit()
        if adjusted_task_ids or suggestion_ids:
            message = "已根据延期、跳过、截止日期和实际用时完成轻量调整。"
        else:
            message = "没有发现需要调整的任务。"
        return DailyPlanAdjustResponse(
            adjusted_task_ids=adjusted_task_ids,
            suggestion_ids=suggestion_ids,
            message=message,
        )

    def _candidate_tasks(self, *, user_id: int, plan_date: date, include_overdue: bool) -> list[TaskItem]:
        query = (
            self.db.query(TaskItem)
            .filter(TaskItem.user_id == user_id)
            .filter(TaskItem.status.in_(["backlog", "pending", "in_progress", "delayed"]))
        )
        if not include_overdue:
            query = query.filter((TaskItem.deadline.is_(None)) | (TaskItem.deadline >= plan_date))
        return query.order_by(TaskItem.deadline.asc(), TaskItem.id.asc()).all()

    def _select_tasks(
        self,
        tasks: list[TaskItem],
        *,
        plan_date: date,
        available_minutes: int,
        max_tasks: int,
        prefer_mixed_categories: bool,
    ) -> list[dict[str, Any]]:
        if not tasks:
            return []
        capacity = int(available_minutes * 1.1)
        sorted_tasks = sorted(tasks, key=lambda task: self._task_sort_key(task, plan_date))
        selected: list[dict[str, Any]] = []
        used_minutes = 0
        hard_count = 0
        used_categories: set[str] = set()

        for task in sorted_tasks:
            if len(selected) >= max_tasks:
                break
            if task.difficulty in {"hard", "very_hard"} and hard_count >= 2 and task.priority != "urgent":
                continue
            category_key = task.category or task.subject or task.project or "uncategorized"
            if (
                prefer_mixed_categories
                and len(selected) >= 2
                and len(used_categories) == 1
                and category_key in used_categories
                and task.priority not in {"urgent", "high"}
            ):
                continue
            planned_minutes = self._planned_minutes(task, remaining=max(capacity - used_minutes, 0))
            if planned_minutes <= 0:
                continue
            if used_minutes + planned_minutes > capacity and selected:
                continue
            selected.append(
                {
                    "task": task,
                    "planned_minutes": planned_minutes,
                    "reason": self._rule_reason(task, plan_date, planned_minutes),
                }
            )
            used_minutes += planned_minutes
            used_categories.add(category_key)
            if task.difficulty in {"hard", "very_hard"}:
                hard_count += 1
        return selected

    @staticmethod
    def _task_sort_key(task: TaskItem, plan_date: date) -> tuple:
        deadline_days = 9999
        overdue = 1
        if task.deadline:
            deadline_days = (task.deadline - plan_date).days
            overdue = 0 if deadline_days < 0 else 1
        status_weight = {"delayed": 0, "in_progress": 1, "pending": 2, "backlog": 3}.get(task.status, 9)
        priority_weight = PRIORITY_WEIGHT.get(task.priority, 2)
        difficulty_weight = DIFFICULTY_WEIGHT.get(task.difficulty or "normal", 1)
        return (overdue, max(deadline_days, -30), priority_weight, status_weight, difficulty_weight, task.id)

    @staticmethod
    def _planned_minutes(task: TaskItem, *, remaining: int) -> int:
        if remaining < 15:
            return 0
        estimated = max(task.estimated_minutes or 60, 15)
        if estimated >= 180 and task.is_splittable:
            return min(90, remaining)
        return min(estimated, remaining)

    @staticmethod
    def _rule_reason(task: TaskItem, plan_date: date, planned_minutes: int) -> str:
        parts = []
        if task.deadline:
            days = (task.deadline - plan_date).days
            if days < 0:
                parts.append("任务已超过截止日期")
            elif days <= 3:
                parts.append("截止日期临近")
        if task.priority in {"urgent", "high"}:
            parts.append(f"优先级为 {task.priority}")
        if task.status == "delayed":
            parts.append("近期曾延期")
        if task.estimated_minutes > planned_minutes:
            parts.append("任务较大，今天先安排小步推进")
        return "；".join(parts) or "按优先级、预计耗时和可用时间选入今日建议"

    @staticmethod
    def _selected_payload(item: dict[str, Any]) -> dict[str, Any]:
        task = item["task"]
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
            "planned_minutes": item["planned_minutes"],
            "rule_reason": item["reason"],
        }

    @staticmethod
    def _summary(selected: list[dict[str, Any]], available_minutes: int) -> str:
        total = sum(item["planned_minutes"] for item in selected)
        if not selected:
            return "任务池中没有可安排任务，请先创建任务或恢复已归档任务。"
        return f"今日建议安排 {len(selected)} 个任务，预计 {total} 分钟，可用时间 {available_minutes} 分钟。"

    def _persist_optional_suggestions(self, user_id: int, suggestions_payload: Any) -> None:
        if not isinstance(suggestions_payload, list):
            return
        for item in suggestions_payload[:20]:
            if not isinstance(item, dict):
                continue
            suggestion = TaskAiSuggestion(
                user_id=user_id,
                task_id=None,
                suggestion_type="today_plan",
                suggestion_content=item,
                accepted=False,
            )
            self.db.add(suggestion)

    def _get_plan(self, user_id: int, daily_plan_id: int) -> DailyPlan:
        plan = (
            self.db.query(DailyPlan)
            .options(selectinload(DailyPlan.tasks).selectinload(DailyPlanTask.task))
            .filter(DailyPlan.id == daily_plan_id, DailyPlan.user_id == user_id)
            .first()
        )
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan not found")
        return plan

    def _read_plan(self, user_id: int, daily_plan_id: int) -> DailyPlanRead:
        return DailyPlanRead.model_validate(self._get_plan(user_id, daily_plan_id))

    def _get_plan_task(self, user_id: int, daily_plan_id: int, daily_plan_task_id: int) -> DailyPlanTask:
        plan_task = (
            self.db.query(DailyPlanTask)
            .options(selectinload(DailyPlanTask.task), selectinload(DailyPlanTask.daily_plan).selectinload(DailyPlan.tasks))
            .join(DailyPlan, DailyPlan.id == DailyPlanTask.daily_plan_id)
            .filter(
                DailyPlan.user_id == user_id,
                DailyPlan.id == daily_plan_id,
                DailyPlanTask.id == daily_plan_task_id,
            )
            .first()
        )
        if plan_task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan task not found")
        return plan_task
