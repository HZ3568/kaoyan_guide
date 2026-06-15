"""calendar task boundary cleanup

Revision ID: 0006_calendar_task_boundary
Revises: 0005_drop_study_planner
Create Date: 2026-06-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_calendar_task_boundary"
down_revision = "0005_drop_study_planner"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table_name)


def upgrade() -> None:
    bind = op.get_bind()
    old_rag_source = "rag_" + "recommendation"
    old_rag_source_short = "rag_" + "recommend"
    old_rag_suggestion = "recommend_" + "from_" + "rag"
    old_rag_suggestion_short = "rag_" + "recommend"
    old_source_suffix = "from_" + "rag"
    old_pending_status = "back" + "log"
    if _table_exists("task_items"):
        bind.execute(
            sa.text("UPDATE task_items SET status = 'pending' WHERE status = :old_status"),
            {"old_status": old_pending_status},
        )
        bind.execute(
            sa.text("UPDATE task_items SET source_type = 'ai_supplement' WHERE source_type IN (:old_full, :old_short)"),
            {"old_full": old_rag_source, "old_short": old_rag_source_short},
        )
        with op.batch_alter_table("task_items") as batch_op:
            batch_op.alter_column(
                "status",
                existing_type=sa.String(length=32),
                server_default="pending",
                existing_nullable=False,
            )
    if _table_exists("task_ai_suggestions"):
        op.execute("UPDATE task_ai_suggestions SET suggestion_type = 'split' WHERE suggestion_type = 'split_task'")
        bind.execute(
            sa.text(
                "UPDATE task_ai_suggestions SET suggestion_type = 'supplement' "
                "WHERE suggestion_type IN (:old_full, :old_short, :old_from)"
            ),
            {"old_full": old_rag_suggestion, "old_short": old_rag_suggestion_short, "old_from": old_source_suffix},
        )


def downgrade() -> None:
    old_pending_status = "back" + "log"
    if _table_exists("task_items"):
        with op.batch_alter_table("task_items") as batch_op:
            batch_op.alter_column(
                "status",
                existing_type=sa.String(length=32),
                server_default=old_pending_status,
                existing_nullable=False,
            )
