import calendar
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session, selectinload

from app.planner.ai_task_assistant import AiTaskAssistant
from app.planner.task_models import DailyPlan, DailyPlanTask, TaskAiSuggestion, TaskFeedback, TaskItem
from app.planner.task_schemas import (
    CalendarDaySummary,
    CalendarMonthSummaryResponse,
    CalendarTaskSuggestion,
    CalendarTaskSupplementRequest,
    CalendarTaskSupplementResponse,
    DailyPlanRead,
)


class CalendarTaskService:
    def __init__(self, db: Session, *, ai_assistant: AiTaskAssistant | None = None) -> None:
        self.db = db
        self.ai_assistant = ai_assistant or AiTaskAssistant()

    def by_date(self, user_id: int, plan_date: date) -> DailyPlanRead | None:
        plan = self._plan_by_date(user_id, plan_date)
        return DailyPlanRead.model_validate(plan) if plan else None

    def month_summary(self, user_id: int, *, year: int, month: int) -> CalendarMonthSummaryResponse:
        _, last_day = calendar.monthrange(year, month)
        start = date(year, month, 1)
        end = date(year, month, last_day)
        summaries = {
            date(year, month, day): CalendarDaySummary(date=date(year, month, day))
            for day in range(1, last_day + 1)
        }
        plans = (
            self.db.query(DailyPlan)
            .options(selectinload(DailyPlan.tasks).selectinload(DailyPlanTask.task))
            .filter(DailyPlan.user_id == user_id, DailyPlan.plan_date >= start, DailyPlan.plan_date <= end)
            .all()
        )
        for plan in plans:
            summary = summaries[plan.plan_date]
            tasks = [item for item in plan.tasks if item.status != "removed"]
            completed = [item for item in tasks if item.status == "completed"]
            summary.task_count += len(tasks)
            summary.completed_count += len(completed)
            summary.estimated_minutes += sum(item.planned_minutes or item.task.estimated_minutes for item in tasks if item.task)
            summary.has_delayed = summary.has_delayed or any(item.status in {"delayed", "skipped"} for item in tasks)
            for item in tasks:
                if item.task and len(summary.titles) < 2:
                    summary.titles.append(item.task.title)

        for summary in summaries.values():
            summary.unfinished_count = max(summary.task_count - summary.completed_count, 0)
            summary.completion_rate = round((summary.completed_count / summary.task_count) * 100) if summary.task_count else 0
        return CalendarMonthSummaryResponse(year=year, month=month, days=list(summaries.values()))

    def supplement(self, user_id: int, payload: CalendarTaskSupplementRequest) -> CalendarTaskSupplementResponse:
        today_tasks = self._tasks_for_date(user_id, payload.plan_date)
        recent_tasks = self._recent_task_payloads(user_id, payload.plan_date, days=30)
        feedback = self._recent_feedback_payloads(user_id, payload.plan_date, days=30)
        request_payload = {
            "date": payload.plan_date,
            "available_minutes": payload.available_minutes,
            "max_new_tasks": payload.max_new_tasks,
            "preferences": payload.preferences.model_dump(),
            "today_tasks": today_tasks,
            "recent_tasks": recent_tasks,
            "feedback": feedback,
        }
        raw_suggestions = self.ai_assistant.supplement_calendar_tasks(request_payload)
        suggestions = [CalendarTaskSuggestion.model_validate(item) for item in raw_suggestions[: payload.max_new_tasks]]
        for suggestion in suggestions:
            self.db.add(
                TaskAiSuggestion(
                    user_id=user_id,
                    task_id=None,
                    suggestion_type="supplement",
                    suggestion_content=suggestion.model_dump(),
                    accepted=False,
                )
            )
        self.db.commit()
        message = "已生成日期任务补充建议，需用户确认后才会创建正式任务。" if suggestions else "当天任务已接近可用时间，未生成补充建议。"
        return CalendarTaskSupplementResponse(suggestions=suggestions, message=message)

    def _plan_by_date(self, user_id: int, plan_date: date) -> DailyPlan | None:
        return (
            self.db.query(DailyPlan)
            .options(selectinload(DailyPlan.tasks).selectinload(DailyPlanTask.task))
            .filter(DailyPlan.user_id == user_id, DailyPlan.plan_date == plan_date)
            .order_by(DailyPlan.created_at.desc(), DailyPlan.id.desc())
            .first()
        )

    def _tasks_for_date(self, user_id: int, plan_date: date) -> list[dict]:
        plan = self._plan_by_date(user_id, plan_date)
        if not plan:
            return []
        return [self._plan_task_payload(item) for item in plan.tasks if item.status != "removed" and item.task]

    def _recent_task_payloads(self, user_id: int, plan_date: date, *, days: int) -> list[dict]:
        start = datetime.combine(plan_date - timedelta(days=days), time.min)
        plan_tasks = (
            self.db.query(DailyPlanTask)
            .options(selectinload(DailyPlanTask.task), selectinload(DailyPlanTask.daily_plan))
            .join(DailyPlan, DailyPlan.id == DailyPlanTask.daily_plan_id)
            .filter(DailyPlan.user_id == user_id, DailyPlan.plan_date >= start, DailyPlan.plan_date <= plan_date)
            .order_by(DailyPlan.plan_date.desc(), DailyPlanTask.id.desc())
            .limit(100)
            .all()
        )
        payloads = [self._plan_task_payload(item) for item in plan_tasks if item.task]
        if payloads:
            return payloads
        tasks = (
            self.db.query(TaskItem)
            .filter(TaskItem.user_id == user_id)
            .filter(TaskItem.status.in_(["pending", "scheduled", "in_progress", "delayed", "overdue"]))
            .order_by(TaskItem.deadline.asc(), TaskItem.id.desc())
            .limit(50)
            .all()
        )
        return [self._task_payload(task) for task in tasks]

    def _recent_feedback_payloads(self, user_id: int, plan_date: date, *, days: int) -> list[dict]:
        start = plan_date - timedelta(days=days)
        feedback_items = (
            self.db.query(TaskFeedback)
            .filter(TaskFeedback.user_id == user_id, TaskFeedback.created_at >= start)
            .order_by(TaskFeedback.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "task_id": item.task_id,
                "daily_plan_task_id": item.daily_plan_task_id,
                "actual_minutes": item.actual_minutes,
                "difficulty_feedback": item.difficulty_feedback,
                "completion_note": item.completion_note,
            }
            for item in feedback_items
        ]

    @staticmethod
    def _plan_task_payload(item: DailyPlanTask) -> dict:
        task = item.task
        return {
            "id": task.id,
            "daily_plan_task_id": item.id,
            "title": task.title,
            "description": task.description,
            "category": task.category,
            "subject": task.subject,
            "project": task.project,
            "priority": task.priority,
            "difficulty": task.difficulty,
            "estimated_minutes": task.estimated_minutes,
            "planned_minutes": item.planned_minutes,
            "deadline": task.deadline,
            "status": item.status,
            "source_type": task.source_type,
        }

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
            "source_type": task.source_type,
        }
