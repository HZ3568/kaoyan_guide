"""drop legacy study planner tables

Revision ID: 0005_drop_study_planner
Revises: 0004_task_checklist
Create Date: 2026-06-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_drop_study_planner"
down_revision = "0004_task_checklist"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return _inspector().has_table(table_name)


def upgrade() -> None:
    for table_name in [
        "daily_tasks",
        "weekly_plans",
        "study_plan_stages",
        "study_plans",
        "study_goals",
        "study_profiles",
    ]:
        if _table_exists(table_name):
            op.drop_table(table_name)


def downgrade() -> None:
    if not _table_exists("study_profiles"):
        op.create_table(
            "study_profiles",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("current_level", sa.Text(), nullable=True),
            sa.Column("daily_available_minutes", sa.Integer(), server_default="180", nullable=False),
            sa.Column("weekly_available_days", sa.Integer(), server_default="6", nullable=False),
            sa.Column("weak_subjects", sa.JSON(), nullable=True),
            sa.Column("is_cross_major", sa.Boolean(), server_default=sa.text("0"), nullable=False),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("study_goals"):
        op.create_table(
            "study_goals",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("target_school", sa.String(length=128), nullable=True),
            sa.Column("target_major", sa.String(length=128), nullable=True),
            sa.Column("exam_subjects", sa.JSON(), nullable=True),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("exam_date", sa.Date(), nullable=False),
            sa.Column("target_score", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("study_plans"):
        op.create_table(
            "study_plans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("goal_id", sa.Integer(), nullable=False),
            sa.Column("profile_id", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("overview", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["goal_id"], ["study_goals.id"]),
            sa.ForeignKeyConstraint(["profile_id"], ["study_profiles.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("study_plan_stages"):
        op.create_table(
            "study_plan_stages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("plan_id", sa.Integer(), nullable=False),
            sa.Column("stage_name", sa.String(length=64), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column("goal", sa.Text(), nullable=True),
            sa.Column("strategy", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["plan_id"], ["study_plans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("weekly_plans"):
        op.create_table(
            "weekly_plans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("plan_id", sa.Integer(), nullable=False),
            sa.Column("stage_id", sa.Integer(), nullable=False),
            sa.Column("week_index", sa.Integer(), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column("weekly_goal", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["plan_id"], ["study_plans.id"]),
            sa.ForeignKeyConstraint(["stage_id"], ["study_plan_stages.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("daily_tasks"):
        op.create_table(
            "daily_tasks",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("plan_id", sa.Integer(), nullable=False),
            sa.Column("weekly_plan_id", sa.Integer(), nullable=False),
            sa.Column("task_date", sa.Date(), nullable=False),
            sa.Column("subject", sa.String(length=64), nullable=True),
            sa.Column("task_type", sa.String(length=32), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("estimated_minutes", sa.Integer(), server_default="60", nullable=False),
            sa.Column("priority", sa.String(length=32), server_default="medium", nullable=False),
            sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
            sa.Column("source", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["plan_id"], ["study_plans.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["weekly_plan_id"], ["weekly_plans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
