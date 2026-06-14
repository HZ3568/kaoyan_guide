from pydantic import BaseModel, Field


class LearningProfileCreate(BaseModel):
    target_school: str | None = None
    target_major: str | None = None
    target_score: int | None = None
    exam_date: str | None = None
    current_level: str | None = None
    weak_subjects: list[str] = Field(default_factory=list)
    daily_available_hours: float = 3.0
    weekly_available_days: int = 6
    learning_preference: str | None = None


class LearningProfileRead(LearningProfileCreate):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


class GeneratePlanRequest(BaseModel):
    profile_id: int | None = None
    start_date: str | None = None
    end_date: str | None = None
    extra_requirements: str | None = None


class LearningPlanRead(BaseModel):
    id: int
    title: str
    start_date: str | None = None
    end_date: str | None = None
    status: str
    plan_json: dict | None = None

    model_config = {"from_attributes": True}
