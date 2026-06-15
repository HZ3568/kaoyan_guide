from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TaskItem(Base):
    __tablename__ = "task_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64), index=True)
    subject: Mapped[str | None] = mapped_column(String(64), index=True)
    project: Mapped[str | None] = mapped_column(String(128), index=True)
    priority: Mapped[str] = mapped_column(String(32), index=True, default="medium", nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(32), index=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    deadline: Mapped[date | None] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(32), index=True, default="backlog", nullable=False)
    parent_task_id: Mapped[int | None] = mapped_column(ForeignKey("task_items.id"), index=True)
    is_splittable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), index=True, default="manual", nullable=False)
    source_ref: Mapped[dict | list | str | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    parent = relationship("TaskItem", remote_side=[id], back_populates="children")
    children = relationship("TaskItem", back_populates="parent")
    daily_plan_tasks = relationship("DailyPlanTask", cascade="all, delete-orphan", back_populates="task")
    ai_suggestions = relationship("TaskAiSuggestion", cascade="all, delete-orphan", back_populates="task")


class DailyPlan(Base):
    __tablename__ = "daily_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    plan_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    available_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True, default="suggested", nullable=False)
    created_by: Mapped[str] = mapped_column(String(32), default="ai", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tasks = relationship("DailyPlanTask", cascade="all, delete-orphan", back_populates="daily_plan")


class DailyPlanTask(Base):
    __tablename__ = "daily_plan_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    daily_plan_id: Mapped[int] = mapped_column(ForeignKey("daily_plans.id"), index=True, nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("task_items.id"), index=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    planned_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    planned_start_time: Mapped[time | None] = mapped_column(Time)
    planned_end_time: Mapped[time | None] = mapped_column(Time)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True, default="suggested", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    daily_plan = relationship("DailyPlan", back_populates="tasks")
    task = relationship("TaskItem", back_populates="daily_plan_tasks")


class TaskAiSuggestion(Base):
    __tablename__ = "task_ai_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("task_items.id"), index=True)
    suggestion_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    suggestion_content: Mapped[dict | list | str] = mapped_column(JSON, nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task = relationship("TaskItem", back_populates="ai_suggestions")


class TaskFeedback(Base):
    __tablename__ = "task_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    daily_plan_task_id: Mapped[int | None] = mapped_column(ForeignKey("daily_plan_tasks.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    actual_minutes: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[str | None] = mapped_column(String(32))
    feedback_text: Mapped[str | None] = mapped_column(Text)
    difficulty_feedback: Mapped[str | None] = mapped_column(String(32))
    completion_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
