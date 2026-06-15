from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.planner.task_models import DailyPlan, DailyPlanTask, TaskAiSuggestion, TaskFeedback, TaskItem


class TaskAdjuster:
    def __init__(self, db: Session) -> None:
        self.db = db

    def adjust(self, *, user_id: int, from_date: date, days: int) -> tuple[list[int], list[int]]:
        window_start = from_date - timedelta(days=max(days, 1))
        feedback_start = datetime.combine(window_start, time.min)
        window_end = from_date + timedelta(days=max(days, 1))
        adjusted_task_ids: list[int] = []
        suggestion_ids: list[int] = []

        overdue_or_delayed = (
            self.db.query(TaskItem)
            .filter(TaskItem.user_id == user_id)
            .filter(TaskItem.status.in_(["delayed", "overdue", "pending", "scheduled", "in_progress"]))
            .filter(TaskItem.deadline.is_not(None), TaskItem.deadline <= window_end)
            .all()
        )
        for task in overdue_or_delayed:
            if task.deadline and task.deadline <= from_date + timedelta(days=3) and task.priority != "urgent":
                task.priority = "urgent"
                adjusted_task_ids.append(task.id)
                suggestion_ids.append(
                    self._add_suggestion(
                        user_id=user_id,
                        task_id=task.id,
                        suggestion_type="adjust_priority",
                        content={
                            "priority": "urgent",
                            "reason": "任务截止日期临近，已提高到 urgent，便于今日计划优先选择。",
                        },
                    ).id
                )

        recent_unfinished = (
            self.db.query(DailyPlanTask)
            .join(DailyPlan, DailyPlan.id == DailyPlanTask.daily_plan_id)
            .filter(DailyPlan.user_id == user_id)
            .filter(DailyPlan.plan_date >= window_start, DailyPlan.plan_date <= from_date)
            .filter(DailyPlanTask.status.in_(["delayed", "skipped"]))
            .all()
        )
        skip_counts: dict[int, int] = {}
        for plan_task in recent_unfinished:
            task = plan_task.task
            if not task:
                continue
            task.status = "delayed" if plan_task.status == "delayed" else task.status
            skip_counts[task.id] = skip_counts.get(task.id, 0) + 1
            adjusted_task_ids.append(task.id)

        for task_id, count in skip_counts.items():
            if count >= 2:
                suggestion_ids.append(
                    self._add_suggestion(
                        user_id=user_id,
                        task_id=task_id,
                        suggestion_type="split",
                        content={
                            "reason": "该任务近期多次延期或跳过，建议拆成更小的 30-60 分钟任务。",
                            "recent_unfinished_count": count,
                        },
                    ).id
                )

        feedback_items = (
            self.db.query(TaskFeedback)
            .filter(TaskFeedback.user_id == user_id)
            .filter(TaskFeedback.created_at >= feedback_start)
            .filter(TaskFeedback.actual_minutes.is_not(None))
            .all()
        )
        task_by_id = {
            task.id: task
            for task in self.db.query(TaskItem)
            .filter(TaskItem.user_id == user_id, TaskItem.id.in_({item.task_id for item in feedback_items}))
            .all()
        }
        for feedback in feedback_items:
            task = task_by_id.get(feedback.task_id)
            if not task or not feedback.actual_minutes:
                continue
            if feedback.actual_minutes >= int(task.estimated_minutes * 1.5):
                task.estimated_minutes = int((task.estimated_minutes + feedback.actual_minutes) / 2)
                adjusted_task_ids.append(task.id)
                suggestion_ids.append(
                    self._add_suggestion(
                        user_id=user_id,
                        task_id=task.id,
                        suggestion_type="estimate_time",
                        content={
                            "estimated_minutes": task.estimated_minutes,
                            "reason": "实际用时显著超过预计用时，已上调后续估算。",
                        },
                    ).id
                )

        return sorted(set(adjusted_task_ids)), sorted(set(suggestion_ids))

    def _add_suggestion(
        self,
        *,
        user_id: int,
        task_id: int,
        suggestion_type: str,
        content: dict,
    ) -> TaskAiSuggestion:
        suggestion = TaskAiSuggestion(
            user_id=user_id,
            task_id=task_id,
            suggestion_type=suggestion_type,
            suggestion_content=content,
            accepted=False,
        )
        self.db.add(suggestion)
        self.db.flush()
        return suggestion
