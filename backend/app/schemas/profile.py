from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.goal import GoalCreate, GoalOut


class UserProfileBase(BaseModel):
    persona_type: str | None = Field(default=None, max_length=64)
    current_stage: str | None = Field(default=None, max_length=128)
    domain: str | None = Field(default=None, max_length=128)
    background_summary: str | None = None
    ability_level: str | None = Field(default=None, max_length=64)
    daily_available_minutes: int | None = Field(default=None, ge=0, le=1440)
    weekly_available_days: int | None = Field(default=None, ge=0, le=7)
    preference_json: dict[str, Any] | list[Any] | None = None
    constraint_json: dict[str, Any] | list[Any] | None = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileOut(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class OnboardingRequest(BaseModel):
    profile: UserProfileCreate
    goal: GoalCreate | None = None


class OnboardingResponse(BaseModel):
    profile: UserProfileOut
    goal: GoalOut | None = None
