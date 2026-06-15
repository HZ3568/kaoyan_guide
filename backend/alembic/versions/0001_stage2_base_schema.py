"""stage2 base schema

Revision ID: 0001_stage2
Revises:
Create Date: 2026-06-14
"""

from collections.abc import Iterable

from alembic import op
import sqlalchemy as sa


revision = "0001_stage2"
down_revision = None
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return _inspector().has_table(table_name)


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(column["name"] == column_name for column in _inspector().get_columns(table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(index["name"] == index_name for index in _inspector().get_indexes(table_name))


def _create_table_if_missing(table_name: str, *columns: sa.Column) -> None:
    if not _table_exists(table_name):
        op.create_table(table_name, *columns)


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if _table_exists(table_name) and not _column_exists(table_name, column.name):
        op.add_column(table_name, column)


def _create_index_if_missing(
    index_name: str,
    table_name: str,
    columns: Iterable[str],
    *,
    unique: bool = False,
) -> None:
    if _table_exists(table_name) and not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, list(columns), unique=unique)


def upgrade() -> None:
    _create_table_if_missing(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), server_default="USER", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=32), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=32), server_default="uploaded", nullable=False),
        sa.Column("source_url", sa.String(length=512), nullable=True),
        sa.Column("subject", sa.String(length=64), nullable=True),
        sa.Column("school", sa.String(length=128), nullable=True),
        sa.Column("major", sa.String(length=128), nullable=True),
        sa.Column("tags_json", sa.JSON(), nullable=True),
        sa.Column("exam_year", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("doc_status", sa.String(length=32), server_default="active", nullable=False),
        sa.Column("parse_status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "document_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_type", sa.String(length=32), server_default="text", nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("position_start", sa.Integer(), nullable=True),
        sa.Column("position_end", sa.Integer(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("token_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("embedding_status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("is_vectorized", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("vector_index_key", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "learning_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("target_school", sa.String(length=128), nullable=True),
        sa.Column("target_major", sa.String(length=128), nullable=True),
        sa.Column("target_score", sa.Integer(), nullable=True),
        sa.Column("exam_date", sa.String(length=32), nullable=True),
        sa.Column("current_level", sa.String(length=64), nullable=True),
        sa.Column("weak_subjects", sa.JSON(), nullable=True),
        sa.Column("daily_available_hours", sa.Float(), server_default="3.0", nullable=False),
        sa.Column("weekly_available_days", sa.Integer(), server_default="6", nullable=False),
        sa.Column("learning_preference", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "learning_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("user_goal", sa.Text(), nullable=True),
        sa.Column("current_foundation", sa.Text(), nullable=True),
        sa.Column("preparation_cycle_days", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.String(length=32), nullable=True),
        sa.Column("end_date", sa.String(length=32), nullable=True),
        sa.Column("plan_type", sa.String(length=32), server_default="generated", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
        sa.Column("plan_json", sa.JSON(), nullable=True),
        sa.Column("generated_content", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["learning_profiles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "learning_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_date", sa.String(length=32), nullable=False),
        sa.Column("subject", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("resource_chunk_ids", sa.JSON(), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), server_default="60", nullable=False),
        sa.Column("priority", sa.String(length=32), server_default="medium", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["learning_plans.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "chat_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), server_default="新会话", nullable=False),
        sa.Column("type", sa.String(length=32), server_default="rag", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("retrieval_context_json", sa.JSON(), nullable=True),
        sa.Column("citations_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "ocr_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("image_path", sa.String(length=512), nullable=False),
        sa.Column("engine", sa.String(length=64), nullable=True),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "ocr_table_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ocr_task_id", sa.Integer(), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("source_image_path", sa.String(length=512), nullable=True),
        sa.Column("source_page_number", sa.Integer(), nullable=True),
        sa.Column("school", sa.String(length=128), nullable=True),
        sa.Column("major", sa.String(length=128), nullable=True),
        sa.Column("research_direction", sa.String(length=255), nullable=True),
        sa.Column("exam_subjects", sa.Text(), nullable=True),
        sa.Column("score_line", sa.String(length=64), nullable=True),
        sa.Column("enrollment_count", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("raw_row_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["ocr_task_id"], ["ocr_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "rag_query_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("filters_json", sa.JSON(), nullable=True),
        sa.Column("retrieved_chunks_json", sa.JSON(), nullable=True),
        sa.Column("model_provider", sa.String(length=64), nullable=True),
        sa.Column("model_name", sa.String(length=128), nullable=True),
        sa.Column("model_answer", sa.Text(), nullable=True),
        sa.Column("hit_source", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    _add_column_if_missing("documents", sa.Column("source", sa.String(length=255), nullable=True))
    _add_column_if_missing("documents", sa.Column("source_url", sa.String(length=512), nullable=True))
    _add_column_if_missing("documents", sa.Column("tags_json", sa.JSON(), nullable=True))
    _add_column_if_missing("documents", sa.Column("description", sa.Text(), nullable=True))

    _add_column_if_missing(
        "document_chunks",
        sa.Column("chunk_type", sa.String(length=32), server_default="text", nullable=False),
    )
    _add_column_if_missing("document_chunks", sa.Column("page_number", sa.Integer(), nullable=True))
    _add_column_if_missing("document_chunks", sa.Column("position_start", sa.Integer(), nullable=True))
    _add_column_if_missing("document_chunks", sa.Column("position_end", sa.Integer(), nullable=True))
    _add_column_if_missing(
        "document_chunks",
        sa.Column("is_vectorized", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )
    _add_column_if_missing(
        "document_chunks",
        sa.Column("vector_index_key", sa.String(length=255), nullable=True),
    )

    _add_column_if_missing("learning_plans", sa.Column("user_goal", sa.Text(), nullable=True))
    _add_column_if_missing("learning_plans", sa.Column("current_foundation", sa.Text(), nullable=True))
    _add_column_if_missing("learning_plans", sa.Column("preparation_cycle_days", sa.Integer(), nullable=True))
    _add_column_if_missing("learning_plans", sa.Column("generated_content", sa.JSON(), nullable=True))

    _create_index_if_missing("ix_users_email", "users", ["email"], unique=True)
    _create_index_if_missing("ix_users_username", "users", ["username"], unique=True)

    _create_index_if_missing("ix_documents_user_id", "documents", ["user_id"])
    _create_index_if_missing("ix_documents_file_type", "documents", ["file_type"])
    _create_index_if_missing("ix_documents_source_type", "documents", ["source_type"])
    _create_index_if_missing("ix_documents_subject", "documents", ["subject"])
    _create_index_if_missing("ix_documents_school", "documents", ["school"])
    _create_index_if_missing("ix_documents_major", "documents", ["major"])
    _create_index_if_missing("ix_documents_parse_status", "documents", ["parse_status"])

    _create_index_if_missing("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    _create_index_if_missing("ix_document_chunks_content_hash", "document_chunks", ["content_hash"])
    _create_index_if_missing("ix_document_chunks_embedding_status", "document_chunks", ["embedding_status"])
    _create_index_if_missing("ix_document_chunks_is_vectorized", "document_chunks", ["is_vectorized"])

    _create_index_if_missing("ix_learning_plans_user_id", "learning_plans", ["user_id"])
    _create_index_if_missing("ix_learning_plans_status", "learning_plans", ["status"])

    _create_index_if_missing("ix_ocr_tasks_user_id", "ocr_tasks", ["user_id"])
    _create_index_if_missing("ix_ocr_tasks_document_id", "ocr_tasks", ["document_id"])
    _create_index_if_missing("ix_ocr_tasks_status", "ocr_tasks", ["status"])
    _create_index_if_missing("ix_ocr_table_records_ocr_task_id", "ocr_table_records", ["ocr_task_id"])
    _create_index_if_missing("ix_ocr_table_records_document_id", "ocr_table_records", ["document_id"])
    _create_index_if_missing("ix_ocr_table_records_school", "ocr_table_records", ["school"])
    _create_index_if_missing("ix_ocr_table_records_major", "ocr_table_records", ["major"])

    _create_index_if_missing("ix_rag_query_logs_user_id", "rag_query_logs", ["user_id"])
    _create_index_if_missing("ix_rag_query_logs_session_id", "rag_query_logs", ["session_id"])
    _create_index_if_missing("ix_rag_query_logs_hit_source", "rag_query_logs", ["hit_source"])


def downgrade() -> None:
    for table_name, column_name in [
        ("learning_plans", "generated_content"),
        ("learning_plans", "preparation_cycle_days"),
        ("learning_plans", "current_foundation"),
        ("learning_plans", "user_goal"),
        ("document_chunks", "vector_index_key"),
        ("document_chunks", "is_vectorized"),
        ("document_chunks", "position_end"),
        ("document_chunks", "position_start"),
        ("document_chunks", "page_number"),
        ("document_chunks", "chunk_type"),
        ("documents", "description"),
        ("documents", "tags_json"),
        ("documents", "source_url"),
        ("documents", "source"),
    ]:
        if _column_exists(table_name, column_name):
            op.drop_column(table_name, column_name)

    for table_name in ["rag_query_logs", "ocr_table_records", "ocr_tasks"]:
        if _table_exists(table_name):
            op.drop_table(table_name)
