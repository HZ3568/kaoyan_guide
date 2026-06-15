from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.planner.daily_plan_service import DailyPlanService
from app.planner.task_models import DailyPlan, DailyPlanTask, TaskAiSuggestion, TaskFeedback, TaskItem
from app.planner.task_schemas import (
    DailyPlanAdjustRequest,
    DailyPlanGenerateRequest,
    DailyPlanTaskStatusUpdate,
    DailyPlanTaskFeedbackCreate,
    TaskItemCreate,
)
from app.planner.task_service import TaskService


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def seed_user(db):
    user = User(username="task-user", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_task_pool_and_daily_plan_services():
    db = make_session()
    try:
        user = seed_user(db)
        task_service = TaskService(db)

        urgent = task_service.create_task(
            user.id,
            TaskItemCreate(
                title="黑马 RAG 和 Agent 项目",
                description="学习项目结构，整理可迁移设计",
                category="项目",
                subject="RAG",
                priority="high",
                difficulty="hard",
                estimated_minutes=180,
                deadline=date.today() + timedelta(days=2),
            ),
        )
        task_service.create_task(
            user.id,
            TaskItemCreate(
                title="在 Typora 中整理八股",
                category="学习",
                subject="八股",
                priority="medium",
                estimated_minutes=60,
            ),
        )

        split = task_service.split_task(user.id, urgent.id)
        assert split.suggestions
        assert db.query(TaskAiSuggestion).count() == 1

        daily_service = DailyPlanService(db)
        generated = daily_service.generate(
            user.id,
            DailyPlanGenerateRequest(date=date.today(), available_minutes=240),
        )
        assert generated.status == "suggested"
        assert generated.suggested_tasks
        assert generated.total_planned_minutes <= 264

        confirmed = daily_service.confirm(user.id, generated.daily_plan_id)
        assert confirmed.status == "confirmed"
        assert confirmed.tasks[0].status == "accepted"

        first_plan_task_id = confirmed.tasks[0].id
        updated = daily_service.update_task_status(
            user.id,
            generated.daily_plan_id,
            first_plan_task_id,
            DailyPlanTaskStatusUpdate(status="completed"),
        )
        assert updated.status == "completed"

        feedback = daily_service.create_feedback(
            user.id,
            generated.daily_plan_id,
            first_plan_task_id,
            DailyPlanTaskFeedbackCreate(actual_minutes=150, difficulty_feedback="hard", completion_note="比预计更难"),
        )
        assert feedback.task_id == updated.task_id
        assert db.query(TaskFeedback).count() == 1

        adjusted = daily_service.adjust(user.id, DailyPlanAdjustRequest(from_date=date.today(), days=7))
        assert "message" in adjusted.model_dump()
    finally:
        db.close()


def test_task_checklist_api_flow():
    old_auto_create_tables = settings.AUTO_CREATE_TABLES
    settings.AUTO_CREATE_TABLES = False
    db = make_session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        auth_payload = {"username": "task-api", "password": "password123"}
        assert client.post("/api/v1/auth/register", json=auth_payload).status_code == 200
        login_res = client.post("/api/v1/auth/login", json=auth_payload)
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        create_res = client.post(
            "/api/v1/tasks",
            json={
                "title": "论文修改、材料准备",
                "description": "整理修改意见并准备补充材料",
                "category": "论文",
                "priority": "urgent",
                "estimated_minutes": 120,
                "deadline": str(date.today() + timedelta(days=1)),
            },
            headers=headers,
        )
        assert create_res.status_code == 200
        task_id = create_res.json()["id"]

        list_res = client.get("/api/v1/tasks?priority=urgent", headers=headers)
        assert list_res.status_code == 200
        assert list_res.json()[0]["id"] == task_id

        split_res = client.post(f"/api/v1/tasks/{task_id}/split", headers=headers)
        assert split_res.status_code == 200
        assert split_res.json()["suggestions"]

        generate_res = client.post(
            "/api/v1/daily-plans/generate",
            json={"date": str(date.today()), "available_minutes": 240, "preferences": {"max_tasks": 5}},
            headers=headers,
        )
        assert generate_res.status_code == 200
        daily_plan_id = generate_res.json()["daily_plan_id"]
        daily_plan_task_id = generate_res.json()["suggested_tasks"][0]["id"]

        confirm_res = client.post(f"/api/v1/daily-plans/{daily_plan_id}/confirm", headers=headers)
        assert confirm_res.status_code == 200
        assert confirm_res.json()["status"] == "confirmed"

        status_res = client.patch(
            f"/api/v1/daily-plans/{daily_plan_id}/tasks/{daily_plan_task_id}/status",
            json={"status": "in_progress"},
            headers=headers,
        )
        assert status_res.status_code == 200
        assert status_res.json()["status"] == "in_progress"

        feedback_res = client.post(
            f"/api/v1/daily-plans/{daily_plan_id}/tasks/{daily_plan_task_id}/feedback",
            json={"actual_minutes": 80, "difficulty_feedback": "normal", "completion_note": "进展正常"},
            headers=headers,
        )
        assert feedback_res.status_code == 200
        assert feedback_res.json()["daily_plan_task_id"] == daily_plan_task_id

        today_res = client.get("/api/v1/daily-plans/today", headers=headers)
        assert today_res.status_code == 200
        assert today_res.json()["id"] == daily_plan_id

        adjust_res = client.post(
            "/api/v1/daily-plans/adjust",
            json={"from_date": str(date.today()), "days": 7},
            headers=headers,
        )
        assert adjust_res.status_code == 200
        assert "message" in adjust_res.json()

        assert db.query(TaskItem).count() == 1
        assert db.query(DailyPlan).count() == 1
        assert db.query(DailyPlanTask).count() == 1
        assert db.query(TaskFeedback).count() == 1
    finally:
        app.dependency_overrides.clear()
        db.close()
        settings.AUTO_CREATE_TABLES = old_auto_create_tables
