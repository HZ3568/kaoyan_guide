from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False, unique=True)
    persona_type: Mapped[str | None] = mapped_column(String(64))
    current_stage: Mapped[str | None] = mapped_column(String(128))
    domain: Mapped[str | None] = mapped_column(String(128), index=True)
    background_summary: Mapped[str | None] = mapped_column(Text)
    ability_level: Mapped[str | None] = mapped_column(String(64))
    daily_available_minutes: Mapped[int | None] = mapped_column(Integer)
    weekly_available_days: Mapped[int | None] = mapped_column(Integer)
    preference_json: Mapped[dict | list | None] = mapped_column(JSON)
    constraint_json: Mapped[dict | list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
