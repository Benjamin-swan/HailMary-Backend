"""add coupons (100% 무료 쿠폰 — 1회용, 무기한)

Revision ID: 007_add_coupons_table
Revises: 006_add_daily_templates
Create Date: 2026-06-04

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "007_add_coupons_table"
down_revision: str | Sequence[str] | None = "006_add_daily_templates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "coupons",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "REDEEMED", name="couponstatus"),
            nullable=False,
        ),
        sa.Column("memo", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_by_user_id", sa.Integer(), nullable=True),
        sa.Column("used_order_id", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["used_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coupons_code"), "coupons", ["code"], unique=True)
    op.create_index(
        op.f("ix_coupons_used_by_user_id"), "coupons", ["used_by_user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_coupons_used_by_user_id"), table_name="coupons")
    op.drop_index(op.f("ix_coupons_code"), table_name="coupons")
    op.drop_table("coupons")
