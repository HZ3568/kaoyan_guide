"""reset domain models for general learning system

Revision ID: 0008_general_reset
Revises:
Create Date: 2026-06-16
"""

from alembic import context, op
import sqlalchemy as sa


revision = "0008_general_reset"
down_revision = None
branch_labels = None
depends_on = None


OLD_TABLES = [
    "task_feedback",
    "task_ai_suggestions",
    "daily_plan_tasks",
    "daily_plans",
    "learning_tasks",
    "learning_plans",
    "learning_profiles",
    "daily_tasks",
    "weekly_plans",
    "study_plan_stages",
    "study_plans",
    "study_goals",
    "study_profiles",
    "document_chunks",
    "ocr_table_records",
    "ocr_tasks",
    "rag_query_logs",
    "chat_messages",
    "chat_sessions",
    "task_execution_sessions",
    "task_items",
    "daily_reviews",
    "documents",
    "knowledge_bases",
    "goals",
    "user_profiles",
]


def _table_exists(table_name: str) -> bool:
    if context.is_offline_mode():
        return False
    return sa.inspect(op.get_bind()).has_table(table_name)


def _drop_table_if_exists(table_name: str) -> None:
    if _table_exists(table_name):
        op.drop_table(table_name)


def upgrade() -> None:
    for table_name in OLD_TABLES:
        _drop_table_if_exists(table_name)

    if not _table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(length=64), nullable=False),
            sa.Column("email", sa.String(length=128), nullable=True),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=32), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_users_id", "users", ["id"])
        op.create_index("ix_users_username", "users", ["username"], unique=True)
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("persona_type", sa.String(length=64), nullable=True),
        sa.Column("current_stage", sa.String(length=128), nullable=True),
        sa.Column("domain", sa.String(length=128), nullable=True),
        sa.Column("background_summary", sa.Text(), nullable=True),
        sa.Column("ability_level", sa.String(length=64), nullable=True),
        sa.Column("daily_available_minutes", sa.Integer(), nullable=True),
        sa.Column("weekly_available_days", sa.Integer(), nullable=True),
        sa.Column("preference_json", sa.JSON(), nullable=True),
        sa.Column("constraint_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_user_profiles_id", "user_profiles", ["id"])
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])
    op.create_index("ix_user_profiles_domain", "user_profiles", ["domain"])

    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("goal_type", sa.String(length=64), nullable=True),
        sa.Column("domain", sa.String(length=128), nullable=True),
        sa.Column("target_result", sa.Text(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("progress", sa.Numeric(5, 2), nullable=False),
        sa.Column("context_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_goals_id", "goals", ["id"])
    op.create_index("ix_goals_user_id", "goals", ["user_id"])
    op.create_index("ix_goals_goal_type", "goals", ["goal_type"])
    op.create_index("ix_goals_domain", "goals", ["domain"])
    op.create_index("ix_goals_deadline", "goals", ["deadline"])
    op.create_index("ix_goals_priority", "goals", ["priority"])
    op.create_index("ix_goals_status", "goals", ["status"])

    op.create_table(
        "knowledge_bases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", sa.String(length=128), nullable=True),
        sa.Column("visibility", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_bases_id", "knowledge_bases", ["id"])
    op.create_index("ix_knowledge_bases_user_id", "knowledge_bases", ["user_id"])
    op.create_index("ix_knowledge_bases_goal_id", "knowledge_bases", ["goal_id"])
    op.create_index("ix_knowledge_bases_domain", "knowledge_bases", ["domain"])

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("knowledge_base_id", sa.Integer(), nullable=True),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("file_type", sa.String(length=32), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("domain", sa.String(length=128), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("tags_json", sa.JSON(), nullable=True),
        sa.Column("parse_status", sa.String(length=32), nullable=True),
        sa.Column("chunk_status", sa.String(length=32), nullable=True),
        sa.Column("embedding_status", sa.String(length=32), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_id", "documents", ["id"])
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_knowledge_base_id", "documents", ["knowledge_base_id"])
    op.create_index("ix_documents_goal_id", "documents", ["goal_id"])
    op.create_index("ix_documents_file_type", "documents", ["file_type"])
    op.create_index("ix_documents_domain", "documents", ["domain"])
    op.create_index("ix_documents_category", "documents", ["category"])
    op.create_index("ix_documents_parse_status", "documents", ["parse_status"])
    op.create_index("ix_documents_chunk_status", "documents", ["chunk_status"])
    op.create_index("ix_documents_embedding_status", "documents", ["embedding_status"])

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("knowledge_base_id", sa.Integer(), nullable=True),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("domain", sa.String(length=128), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("embedding_id", sa.String(length=255), nullable=True),
        sa.Column("embedding_status", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_chunks_id", "document_chunks", ["id"])
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_document_chunks_user_id", "document_chunks", ["user_id"])
    op.create_index("ix_document_chunks_knowledge_base_id", "document_chunks", ["knowledge_base_id"])
    op.create_index("ix_document_chunks_goal_id", "document_chunks", ["goal_id"])
    op.create_index("ix_document_chunks_content_hash", "document_chunks", ["content_hash"])
    op.create_index("ix_document_chunks_domain", "document_chunks", ["domain"])
    op.create_index("ix_document_chunks_category", "document_chunks", ["category"])
    op.create_index("ix_document_chunks_embedding_id", "document_chunks", ["embedding_id"])
    op.create_index("ix_document_chunks_embedding_status", "document_chunks", ["embedding_status"])

    op.create_table(
        "rag_query_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("knowledge_base_id", sa.Integer(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("top_k", sa.Integer(), nullable=False),
        sa.Column("filters_json", sa.JSON(), nullable=True),
        sa.Column("sources_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rag_query_logs_id", "rag_query_logs", ["id"])
    op.create_index("ix_rag_query_logs_user_id", "rag_query_logs", ["user_id"])
    op.create_index("ix_rag_query_logs_goal_id", "rag_query_logs", ["goal_id"])
    op.create_index("ix_rag_query_logs_knowledge_base_id", "rag_query_logs", ["knowledge_base_id"])

    op.create_table(
        "task_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(length=128), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("task_type", sa.String(length=64), nullable=True),
        sa.Column("planned_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("actual_minutes", sa.Integer(), nullable=True),
        sa.Column("actual_start_time", sa.DateTime(), nullable=True),
        sa.Column("actual_end_time", sa.DateTime(), nullable=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("ai_reason", sa.Text(), nullable=True),
        sa.Column("context_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_items_id", "task_items", ["id"])
    op.create_index("ix_task_items_user_id", "task_items", ["user_id"])
    op.create_index("ix_task_items_goal_id", "task_items", ["goal_id"])
    op.create_index("ix_task_items_domain", "task_items", ["domain"])
    op.create_index("ix_task_items_category", "task_items", ["category"])
    op.create_index("ix_task_items_task_type", "task_items", ["task_type"])
    op.create_index("ix_task_items_planned_date", "task_items", ["planned_date"])
    op.create_index("ix_task_items_status", "task_items", ["status"])
    op.create_index("ix_task_items_priority", "task_items", ["priority"])
    op.create_index("ix_task_items_source_type", "task_items", ["source_type"])

    op.create_table(
        "task_execution_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["task_items.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_execution_sessions_id", "task_execution_sessions", ["id"])
    op.create_index("ix_task_execution_sessions_user_id", "task_execution_sessions", ["user_id"])
    op.create_index("ix_task_execution_sessions_task_id", "task_execution_sessions", ["task_id"])
    op.create_index("ix_task_execution_sessions_status", "task_execution_sessions", ["status"])

    op.create_table(
        "daily_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column("completion_rate", sa.Integer(), nullable=False),
        sa.Column("total_estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("total_actual_minutes", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("problems", sa.Text(), nullable=True),
        sa.Column("adjustment_suggestion", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_daily_reviews_id", "daily_reviews", ["id"])
    op.create_index("ix_daily_reviews_user_id", "daily_reviews", ["user_id"])
    op.create_index("ix_daily_reviews_goal_id", "daily_reviews", ["goal_id"])
    op.create_index("ix_daily_reviews_review_date", "daily_reviews", ["review_date"])


def downgrade() -> None:
    for table_name in [
        "daily_reviews",
        "task_execution_sessions",
        "task_items",
        "rag_query_logs",
        "document_chunks",
        "documents",
        "knowledge_bases",
        "goals",
        "user_profiles",
    ]:
        _drop_table_if_exists(table_name)
