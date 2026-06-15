"""stage6 task checklist schema

Revision ID: 0004_task_checklist
Revises: 0003_drop_legacy
Create Date: 2026-06-15
"""

from collections.abc import Iterable

from alembic import op
import sqlalchemy as sa


revision = "0004_task_checklist"
down_revision = "0003_drop_legacy"
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


def _create_index_if_missing(
    index_name: str,
    table_name: str,
    columns: Iterable[str],
    *,
    unique: bool = False,
) -> None:
    if _table_exists(table_name) and not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, list(columns), unique=unique)


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if _table_exists(table_name) and not _column_exists(table_name, column.name):
        op.add_column(table_name, column)


def _drop_task_feedback_task_fk_if_present() -> None:
    if not _table_exists("task_feedback"):
        return
    for fk in _inspector().get_foreign_keys("task_feedback"):
        if fk.get("constrained_columns") == ["task_id"] and fk.get("name"):
            op.drop_constraint(fk["name"], "task_feedback", type_="foreignkey")


def upgrade() -> None:
    _create_table_if_missing(
        "task_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("subject", sa.String(length=64), nullable=True),
        sa.Column("project", sa.String(length=128), nullable=True),
        sa.Column("priority", sa.String(length=32), server_default="medium", nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), server_default="60", nullable=False),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="backlog", nullable=False),
        sa.Column("parent_task_id", sa.Integer(), nullable=True),
        sa.Column("is_splittable", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("is_ai_generated", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("source_type", sa.String(length=32), server_default="manual", nullable=False),
        sa.Column("source_ref", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["parent_task_id"], ["task_items.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "daily_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("available_minutes", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="suggested", nullable=False),
        sa.Column("created_by", sa.String(length=32), server_default="ai", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "daily_plan_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("daily_plan_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("planned_minutes", sa.Integer(), server_default="60", nullable=False),
        sa.Column("planned_start_time", sa.Time(), nullable=True),
        sa.Column("planned_end_time", sa.Time(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="suggested", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["daily_plan_id"], ["daily_plans.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["task_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    _create_table_if_missing(
        "task_ai_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("suggestion_type", sa.String(length=32), nullable=False),
        sa.Column("suggestion_content", sa.JSON(), nullable=False),
        sa.Column("accepted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["task_items.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    if _table_exists("task_feedback"):
        _drop_task_feedback_task_fk_if_present()
        _add_column_if_missing("task_feedback", sa.Column("daily_plan_task_id", sa.Integer(), nullable=True))
        _add_column_if_missing("task_feedback", sa.Column("difficulty_feedback", sa.String(length=32), nullable=True))
        _add_column_if_missing("task_feedback", sa.Column("completion_note", sa.Text(), nullable=True))
    else:
        op.create_table(
            "task_feedback",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("task_id", sa.Integer(), nullable=False),
            sa.Column("daily_plan_task_id", sa.Integer(), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("actual_minutes", sa.Integer(), nullable=True),
            sa.Column("difficulty", sa.String(length=32), nullable=True),
            sa.Column("feedback_text", sa.Text(), nullable=True),
            sa.Column("difficulty_feedback", sa.String(length=32), nullable=True),
            sa.Column("completion_note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["daily_plan_task_id"], ["daily_plan_tasks.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    _create_index_if_missing("ix_task_items_user_id", "task_items", ["user_id"])
    _create_index_if_missing("ix_task_items_category", "task_items", ["category"])
    _create_index_if_missing("ix_task_items_subject", "task_items", ["subject"])
    _create_index_if_missing("ix_task_items_project", "task_items", ["project"])
    _create_index_if_missing("ix_task_items_priority", "task_items", ["priority"])
    _create_index_if_missing("ix_task_items_difficulty", "task_items", ["difficulty"])
    _create_index_if_missing("ix_task_items_deadline", "task_items", ["deadline"])
    _create_index_if_missing("ix_task_items_status", "task_items", ["status"])
    _create_index_if_missing("ix_task_items_parent_task_id", "task_items", ["parent_task_id"])
    _create_index_if_missing("ix_task_items_source_type", "task_items", ["source_type"])
    _create_index_if_missing("ix_daily_plans_user_id", "daily_plans", ["user_id"])
    _create_index_if_missing("ix_daily_plans_plan_date", "daily_plans", ["plan_date"])
    _create_index_if_missing("ix_daily_plans_status", "daily_plans", ["status"])
    _create_index_if_missing("ix_daily_plan_tasks_daily_plan_id", "daily_plan_tasks", ["daily_plan_id"])
    _create_index_if_missing("ix_daily_plan_tasks_task_id", "daily_plan_tasks", ["task_id"])
    _create_index_if_missing("ix_daily_plan_tasks_status", "daily_plan_tasks", ["status"])
    _create_index_if_missing("ix_task_ai_suggestions_user_id", "task_ai_suggestions", ["user_id"])
    _create_index_if_missing("ix_task_ai_suggestions_task_id", "task_ai_suggestions", ["task_id"])
    _create_index_if_missing("ix_task_ai_suggestions_suggestion_type", "task_ai_suggestions", ["suggestion_type"])
    _create_index_if_missing("ix_task_feedback_daily_plan_task_id", "task_feedback", ["daily_plan_task_id"])

    if _table_exists("task_feedback"):
        foreign_keys = _inspector().get_foreign_keys("task_feedback")
        has_daily_plan_task_fk = any(fk.get("constrained_columns") == ["daily_plan_task_id"] for fk in foreign_keys)
        if not has_daily_plan_task_fk:
            op.create_foreign_key(
                "fk_task_feedback_daily_plan_task_id",
                "task_feedback",
                "daily_plan_tasks",
                ["daily_plan_task_id"],
                ["id"],
            )


def downgrade() -> None:
    if _table_exists("task_feedback"):
        for fk in _inspector().get_foreign_keys("task_feedback"):
            if fk.get("constrained_columns") == ["daily_plan_task_id"] and fk.get("name"):
                op.drop_constraint(fk["name"], "task_feedback", type_="foreignkey")
        for column_name in ["completion_note", "difficulty_feedback", "daily_plan_task_id"]:
            if _column_exists("task_feedback", column_name):
                op.drop_column("task_feedback", column_name)

    for table_name in ["task_ai_suggestions", "daily_plan_tasks", "daily_plans", "task_items"]:
        if _table_exists(table_name):
            op.drop_table(table_name)
