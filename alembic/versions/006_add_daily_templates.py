"""add daily_templates (깨비 일일사주 본문 템플릿 70장)

Revision ID: 006_add_daily_templates
Revises: f3b6ba2f1b8e
Create Date: 2026-05-29

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "006_add_daily_templates"
down_revision: str | Sequence[str] | None = "f3b6ba2f1b8e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "daily_templates",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("sipseong", sa.String(length=10), nullable=False),
        sa.Column("branch_rel", sa.String(length=10), nullable=False),
        sa.Column("body", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sipseong", "branch_rel", name="uq_daily_template_keys"),
    )
    op.create_index("ix_daily_templates_sipseong", "daily_templates", ["sipseong"])
    op.create_index("ix_daily_templates_branch_rel", "daily_templates", ["branch_rel"])


def downgrade() -> None:
    op.drop_index("ix_daily_templates_branch_rel", table_name="daily_templates")
    op.drop_index("ix_daily_templates_sipseong", table_name="daily_templates")
    op.drop_table("daily_templates")
