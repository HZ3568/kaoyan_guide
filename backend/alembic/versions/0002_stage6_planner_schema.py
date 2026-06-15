"""stage6 planner schema

Revision ID: 0002_stage6
Revises: 0001_stage2
Create Date: 2026-06-15
"""

from collections.abc import Iterable

from alembic import op
import sqlalchemy as sa


revision = "0002_stage6"
down_revision = "0001_stage2"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return _inspector().has_table(table_name)


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(index["name"] == index_name for index in _inspector().get_indexes(table_name))


def _create_table_if_missing(table_name: str, *columns: sa.Column) -> None:
    if not _table_exists(table_name):
        op.create_table(table_name, *columns)


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
    _create_table_if_missing(
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
    _create_table_if_missing(
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
    _create_table_if_missing(
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
    _create_table_if_missing(
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
    _create_table_if_missing(
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
    _create_table_if_missing(
        "task_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("actual_minutes", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=32), nullable=True),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["daily_tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    _create_index_if_missing("ix_study_profiles_user_id", "study_profiles", ["user_id"])
    _create_index_if_missing("ix_study_goals_user_id", "study_goals", ["user_id"])
    _create_index_if_missing("ix_study_plans_user_id", "study_plans", ["user_id"])
    _create_index_if_missing("ix_study_plans_goal_id", "study_plans", ["goal_id"])
    _create_index_if_missing("ix_study_plans_profile_id", "study_plans", ["profile_id"])
    _create_index_if_missing("ix_study_plans_status", "study_plans", ["status"])
    _create_index_if_missing("ix_study_plan_stages_plan_id", "study_plan_stages", ["plan_id"])
    _create_index_if_missing("ix_weekly_plans_plan_id", "weekly_plans", ["plan_id"])
    _create_index_if_missing("ix_weekly_plans_stage_id", "weekly_plans", ["stage_id"])
    _create_index_if_missing("ix_daily_tasks_user_id", "daily_tasks", ["user_id"])
    _create_index_if_missing("ix_daily_tasks_plan_id", "daily_tasks", ["plan_id"])
    _create_index_if_missing("ix_daily_tasks_weekly_plan_id", "daily_tasks", ["weekly_plan_id"])
    _create_index_if_missing("ix_daily_tasks_task_date", "daily_tasks", ["task_date"])
    _create_index_if_missing("ix_daily_tasks_task_type", "daily_tasks", ["task_type"])
    _create_index_if_missing("ix_daily_tasks_status", "daily_tasks", ["status"])
    _create_index_if_missing("ix_task_feedback_task_id", "task_feedback", ["task_id"])
    _create_index_if_missing("ix_task_feedback_user_id", "task_feedback", ["user_id"])


def downgrade() -> None:
    for table_name in [
        "task_feedback",
        "daily_tasks",
        "weekly_plans",
        "study_plan_stages",
        "study_plans",
        "study_goals",
        "study_profiles",
    ]:
        if _table_exists(table_name):
            op.drop_table(table_name)
