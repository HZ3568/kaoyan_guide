from datetime import date, datetime, timedelta
from math import ceil

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.planner.ai_task_assistant import AiTaskAssistant
from app.planner.task_models import TaskExecutionSession, TaskItem
from app.planner.task_schemas import (
    CalendarDaySummary,
    CalendarMonthSummaryResponse,
    TaskCompleteRequest,
    TaskItemCreate,
    TaskItemUpdate,
    TaskOptimizeRequest,
    TaskOptimizeResponse,
    TaskSupplementRequest,
    TaskSupplementResponse,
    TaskSuggestion,
)


class TaskService:
    def __init__(self, db: Session, *, ai_assistant: AiTaskAssistant | None = None) -> None:
        self.db = db
        self.ai_assistant = ai_assistant or AiTaskAssistant()

    def create_task(self, user_id: int, payload: TaskItemCreate) -> TaskItem:
        task = TaskItem(user_id=user_id, **payload.model_dump())
        if task.planned_date and task.status == "pending":
            task.status = "scheduled"
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_tasks(
        self,
        user_id: int,
        *,
        goal_id: int | None = None,
        planned_date: date | None = None,
        status_filter: str | None = None,
        category: str | None = None,
    ) -> list[TaskItem]:
        query = self.db.query(TaskItem).filter(TaskItem.user_id == user_id)
        if goal_id is not None:
            query = query.filter(TaskItem.goal_id == goal_id)
        if planned_date is not None:
            query = query.filter(TaskItem.planned_date == planned_date)
        if status_filter:
            query = query.filter(TaskItem.status == status_filter)
        if category:
            query = query.filter(TaskItem.category == category)
        return query.order_by(TaskItem.planned_date.asc(), TaskItem.id.desc()).all()

    def get_task(self, user_id: int, task_id: int) -> TaskItem:
        task = self.db.query(TaskItem).filter(TaskItem.id == task_id, TaskItem.user_id == user_id).first()
        if not task:
            raise NotFoundError("Task not found")
        return task

    def update_task(self, user_id: int, task_id: int, payload: TaskItemUpdate) -> TaskItem:
        task = self.get_task(user_id, task_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_status(self, user_id: int, task_id: int, status: str) -> TaskItem:
        task = self.get_task(user_id, task_id)
        task.status = status
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, user_id: int, task_id: int) -> TaskItem:
        task = self.get_task(user_id, task_id)
        task.status = "archived"
        self.db.commit()
        self.db.refresh(task)
        return task

    def postpone_task(self, user_id: int, task_id: int) -> TaskItem:
        task = self.get_task(user_id, task_id)
        if self._running_session(user_id, task_id=task.id):
            raise BadRequestError("当前任务正在计时，请先完成或暂停后再延期")
        task.status = "delayed"
        task.planned_date = (task.planned_date or date.today()) + timedelta(days=1)
        self.db.commit()
        self.db.refresh(task)
        return task

    def start_task(self, user_id: int, task_id: int) -> TaskExecutionSession:
        task = self.get_task(user_id, task_id)
        running = self._running_session(user_id)
        if running and running.task_id != task_id:
            raise BadRequestError("当前已有任务正在计时，请先完成当前任务")
        if running and running.task_id == task_id:
            return running
        now = datetime.utcnow()
        task.status = "in_progress"
        task.actual_start_time = task.actual_start_time or now
        session = TaskExecutionSession(user_id=user_id, task_id=task.id, started_at=now, status="running")
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def pause_task(self, user_id: int, task_id: int) -> TaskExecutionSession:
        task = self.get_task(user_id, task_id)
        session = self._running_session(user_id, task_id=task.id)
        if not session:
            raise NotFoundError("Running task session not found")
        now = datetime.utcnow()
        session.ended_at = now
        session.duration_minutes = max(0, ceil((now - session.started_at).total_seconds() / 60))
        session.status = "paused"
        task.status = "pending"
        self.db.commit()
        self.db.refresh(session)
        return session

    def complete_task(self, user_id: int, task_id: int, payload: TaskCompleteRequest | None = None) -> TaskItem:
        task = self.get_task(user_id, task_id)
        now = datetime.utcnow()
        session = self._running_session(user_id, task_id=task.id)
        if session:
            session.ended_at = now
            session.duration_minutes = max(0, ceil((now - session.started_at).total_seconds() / 60))
            session.status = "completed"
            actual_minutes = session.duration_minutes
        else:
            actual_minutes = payload.actual_minutes if payload and payload.actual_minutes is not None else 0
        task.status = "completed"
        task.actual_minutes = actual_minutes
        task.actual_end_time = now
        task.actual_start_time = task.actual_start_time or (session.started_at if session else None)
        self.db.commit()
        self.db.refresh(task)
        return task

    def optimize_task(self, user_id: int, payload: TaskOptimizeRequest) -> TaskOptimizeResponse:
        data = payload.model_dump()
        suggestion = self.ai_assistant.optimize_task(data)
        return TaskOptimizeResponse(**suggestion)

    def supplement_tasks(self, user_id: int, payload: TaskSupplementRequest) -> TaskSupplementResponse:
        today_tasks = [
            self._task_payload(task)
            for task in self.list_tasks(user_id, goal_id=payload.goal_id, planned_date=payload.planned_date)
            if task.status not in {"completed", "archived", "cancelled"}
        ]
        recent_start = payload.planned_date - timedelta(days=30)
        recent_query = (
            self.db.query(TaskItem)
            .filter(TaskItem.user_id == user_id)
            .filter(TaskItem.planned_date >= recent_start, TaskItem.planned_date <= payload.planned_date)
        )
        if payload.goal_id is not None:
            recent_query = recent_query.filter(TaskItem.goal_id == payload.goal_id)
        recent_tasks = recent_query.order_by(TaskItem.planned_date.desc(), TaskItem.id.desc()).limit(100).all()
        request_payload = {
            **payload.model_dump(),
            "today_tasks": today_tasks,
            "recent_tasks": [self._task_payload(task) for task in recent_tasks],
        }
        raw = self.ai_assistant.supplement_tasks(request_payload)
        suggestions = [TaskSuggestion.model_validate(item) for item in raw[: payload.max_new_tasks]]
        message = "已生成任务补充建议，用户确认后才会创建正式任务。"
        if self.ai_assistant.last_error:
            message = f"模型调用失败，已使用规则兜底：{self.ai_assistant.last_error}"
        return TaskSupplementResponse(suggestions=suggestions, message=message)

    def month_summary(
        self,
        user_id: int,
        *,
        year: int,
        month: int,
        goal_id: int | None = None,
    ) -> CalendarMonthSummaryResponse:
        import calendar

        _, last_day = calendar.monthrange(year, month)
        summaries = {
            date(year, month, day): CalendarDaySummary(date=date(year, month, day))
            for day in range(1, last_day + 1)
        }
        query = (
            self.db.query(TaskItem)
            .filter(TaskItem.user_id == user_id)
            .filter(TaskItem.planned_date >= date(year, month, 1), TaskItem.planned_date <= date(year, month, last_day))
            .filter(TaskItem.status != "archived")
        )
        if goal_id is not None:
            query = query.filter(TaskItem.goal_id == goal_id)
        tasks = query.all()
        for task in tasks:
            if not task.planned_date or task.planned_date not in summaries:
                continue
            summary = summaries[task.planned_date]
            summary.task_count += 1
            summary.estimated_minutes += task.estimated_minutes or 0
            summary.actual_minutes += task.actual_minutes or 0
            summary.has_delayed = summary.has_delayed or task.status == "delayed"
            if task.status == "completed":
                summary.completed_count += 1
            if len(summary.titles) < 2:
                summary.titles.append(task.content[:24])
        for summary in summaries.values():
            summary.unfinished_count = max(summary.task_count - summary.completed_count, 0)
            summary.completion_rate = round((summary.completed_count / summary.task_count) * 100) if summary.task_count else 0
        return CalendarMonthSummaryResponse(year=year, month=month, days=list(summaries.values()))

    def _running_session(self, user_id: int, *, task_id: int | None = None) -> TaskExecutionSession | None:
        query = self.db.query(TaskExecutionSession).filter(
            TaskExecutionSession.user_id == user_id,
            TaskExecutionSession.status == "running",
        )
        if task_id is not None:
            query = query.filter(TaskExecutionSession.task_id == task_id)
        return query.order_by(TaskExecutionSession.started_at.desc()).first()

    @staticmethod
    def _task_payload(task: TaskItem) -> dict:
        return {
            "id": task.id,
            "goal_id": task.goal_id,
            "content": task.content,
            "domain": task.domain,
            "category": task.category,
            "task_type": task.task_type,
            "planned_date": task.planned_date,
            "status": task.status,
            "priority": task.priority,
            "estimated_minutes": task.estimated_minutes,
            "actual_minutes": task.actual_minutes,
            "source_type": task.source_type,
        }
