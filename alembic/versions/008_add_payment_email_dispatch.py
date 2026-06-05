"""payments에 결과지 메일 확정-후-발송 컬럼 추가

email_confirmed_at — FE 이메일 확인 모달 확정 시각
result_email_sent_at — 결과지 링크 메일 발송 시각 (NULL=미발송, 스위퍼 폴백 대상)

기존 행(이미 발송된 결제)은 result_email_sent_at을 approved_at으로 backfill —
스위퍼가 과거 결제에 중복 발송하지 않도록.

Revision ID: 008_add_payment_email_dispatch
Revises: 007_add_coupons_table
Create Date: 2026-06-05

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "008_add_payment_email_dispatch"
down_revision: str | Sequence[str] | None = "007_add_coupons_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "payments",
        sa.Column("email_confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "payments",
        sa.Column("result_email_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    # 기존 결제는 구 설계(즉시 발송)로 이미 메일이 나갔음 — 스위퍼 중복 발송 방지 backfill.
    op.execute(
        "UPDATE payments SET result_email_sent_at = approved_at "
        "WHERE status = 'DONE' AND result_email_sent_at IS NULL"
    )


def downgrade() -> None:
    op.drop_column("payments", "result_email_sent_at")
    op.drop_column("payments", "email_confirmed_at")
