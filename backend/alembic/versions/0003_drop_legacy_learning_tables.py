"""drop legacy learning tables

Revision ID: 0003_drop_legacy
Revises: 0002_stage6
Create Date: 2026-06-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_drop_legacy"
down_revision = "0002_stage6"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return _inspector().has_table(table_name)


def upgrade() -> None:
    for table_name in ["learning_tasks", "learning_plans", "learning_profiles"]:
        if _table_exists(table_name):
            op.drop_table(table_name)


def downgrade() -> None:
    if not _table_exists("learning_profiles"):
        op.create_table(
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
    if not _table_exists("learning_plans"):
        op.create_table(
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
    if not _table_exists("learning_tasks"):
        op.create_table(
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
