from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.database import Base


def test_stage2_schema_tables_and_columns():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    expected_columns = {
        "documents": {
            "id",
            "title",
            "source",
            "file_type",
            "file_path",
            "subject",
            "school",
            "major",
            "tags_json",
            "parse_status",
            "created_at",
        },
        "document_chunks": {
            "id",
            "document_id",
            "content",
            "chunk_type",
            "page_number",
            "token_count",
            "embedding_status",
            "is_vectorized",
        },
        "ocr_tasks": {
            "id",
            "image_path",
            "raw_json",
            "status",
            "created_at",
        },
        "ocr_table_records": {
            "id",
            "school",
            "major",
            "research_direction",
            "exam_subjects",
            "score_line",
            "enrollment_count",
            "document_id",
        },
        "rag_query_logs": {
            "id",
            "question",
            "retrieved_chunks_json",
            "model_answer",
            "hit_source",
            "created_at",
        },
        "learning_plans": {
            "id",
            "user_goal",
            "current_foundation",
            "preparation_cycle_days",
            "generated_content",
            "created_at",
        },
    }

    for table_name, columns in expected_columns.items():
        assert table_name in inspector.get_table_names()
        actual_columns = {column["name"] for column in inspector.get_columns(table_name)}
        assert columns <= actual_columns
