from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.learning_plan import LearningPlan, LearningTask
from app.models.learning_profile import LearningProfile
from app.schemas.planner import GeneratePlanRequest


class PlannerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_profile(self, user_id: int, payload):
        profile = LearningProfile(user_id=user_id, **payload.model_dump())
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def generate_plan(self, user_id: int, payload: GeneratePlanRequest):
        start = date.fromisoformat(payload.start_date) if payload.start_date else date.today()
        end = date.fromisoformat(payload.end_date) if payload.end_date else start + timedelta(days=30)
        plan_json = {
            "stages": [
                {
                    "name": "基础启动阶段",
                    "start_date": str(start),
                    "end_date": str(end),
                    "goal": "建立复习节奏，完成资料梳理与第一轮基础学习。",
                    "tasks": [
                        {
                            "date": str(start + timedelta(days=i)),
                            "subject": "公共课/专业课",
                            "title": f"第 {i + 1} 天学习任务",
                            "estimated_minutes": 120,
                            "description": "根据知识库资料完成当天学习，并记录薄弱点。",
                        }
                        for i in range(min((end - start).days + 1, 7))
                    ],
                }
            ]
        }
        plan = LearningPlan(
            user_id=user_id,
            profile_id=payload.profile_id,
            title="考研学习计划初稿",
            start_date=str(start),
            end_date=str(end),
            plan_json=plan_json,
        )
        self.db.add(plan)
        self.db.flush()
        for task in plan_json["stages"][0]["tasks"]:
            self.db.add(
                LearningTask(
                    plan_id=plan.id,
                    user_id=user_id,
                    task_date=task["date"],
                    subject=task["subject"],
                    title=task["title"],
                    description=task["description"],
                    estimated_minutes=task["estimated_minutes"],
                )
            )
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def list_plans(self, user_id: int):
        return self.db.query(LearningPlan).filter(LearningPlan.user_id == user_id).all()

    def today_tasks(self, user_id: int):
        today = str(date.today())
        return self.db.query(LearningTask).filter(LearningTask.user_id == user_id, LearningTask.task_date == today).all()
