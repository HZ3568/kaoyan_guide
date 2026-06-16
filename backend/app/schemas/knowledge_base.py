from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Visibility = Literal["private", "shared", "public"]


class KnowledgeBaseBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    domain: str | None = Field(default=None, max_length=128)
    visibility: Visibility = "private"
    goal_id: int | None = None


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    domain: str | None = Field(default=None, max_length=128)
    visibility: Visibility | None = None
    goal_id: int | None = None


class KnowledgeBaseOut(KnowledgeBaseBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
