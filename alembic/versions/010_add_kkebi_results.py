"""깨비 일일운세 저장 (HM-BE-79) — kkebi_results 테이블

로그인 사용자의 당일 깨비 운세 저장본. UNIQUE(account_id, cycle_id)로 계정·일자당 1건.
당일(cycle_id)만 보관 — 다음 cycle 저장 시 과거 행 삭제 + today 조회 404로 자연 소멸.

Revision ID: 010_add_kkebi_results
Revises: 009_add_accounts_and_links
Create Date: 2026-06-08

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "010_add_kkebi_results"
down_revision: str | Sequence[str] | None = "009_add_accounts_and_links"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "kkebi_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("cycle_id", sa.String(length=8), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], name="fk_kkebi_results_account_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "cycle_id", name="uq_kkebi_results_account_cycle"),
    )
    op.create_index("ix_kkebi_results_account_id", "kkebi_results", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_kkebi_results_account_id", table_name="kkebi_results")
    op.drop_table("kkebi_results")
