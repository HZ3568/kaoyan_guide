from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OcrTask(Base):
    __tablename__ = "ocr_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), index=True, nullable=True)
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    engine: Mapped[str | None] = mapped_column(String(64))
    raw_json: Mapped[dict | list | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), index=True, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    table_records = relationship("OcrTableRecord", back_populates="ocr_task")


class OcrTableRecord(Base):
    __tablename__ = "ocr_table_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ocr_task_id: Mapped[int | None] = mapped_column(ForeignKey("ocr_tasks.id"), index=True, nullable=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), index=True, nullable=True)
    source_image_path: Mapped[str | None] = mapped_column(String(512))
    source_page_number: Mapped[int | None] = mapped_column(Integer)
    school: Mapped[str | None] = mapped_column(String(128), index=True)
    major: Mapped[str | None] = mapped_column(String(128), index=True)
    research_direction: Mapped[str | None] = mapped_column(String(255))
    exam_subjects: Mapped[str | None] = mapped_column(Text)
    score_line: Mapped[str | None] = mapped_column(String(64))
    enrollment_count: Mapped[int | None] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text)
    raw_row_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ocr_task = relationship("OcrTask", back_populates="table_records")
