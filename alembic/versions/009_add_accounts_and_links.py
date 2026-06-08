"""소셜 로그인 (HM-BE-77) — accounts 테이블 + payments/users 계정 귀속 컬럼

accounts — 카카오/구글 소셜 계정. (provider, provider_user_id) 자연키.
  last_* 컬럼은 '마지막 사용' 사주 입력값 스냅샷 (설문 prefill용, P5 배선).
payments.account_id — NULL=비로그인 결제. 로그인 시 인증 이메일 매칭 backfill.
users.account_id — NULL=비로그인 제출. 로그인 상태 무료사주 제출 시 연결 (P5).

Revision ID: 009_add_accounts_and_links
Revises: 008_add_payment_email_dispatch
Create Date: 2026-06-07

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "009_add_accounts_and_links"
down_revision: str | Sequence[str] | None = "008_add_payment_email_dispatch"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.Enum("kakao", "google", name="provider"), nullable=False),
        sa.Column("provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("nickname", sa.String(length=100), nullable=True),
        sa.Column("profile_image_url", sa.String(length=500), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("last_birth_date", sa.Date(), nullable=True),
        sa.Column(
            "last_calendar_type",
            sa.Enum("solar", "lunar", name="calendartype"),
            nullable=True,
        ),
        sa.Column("last_birth_time", sa.Time(), nullable=True),
        sa.Column("last_birth_time_unknown", sa.Boolean(), nullable=True),
        sa.Column("last_gender", sa.Enum("male", "female", name="gender"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_accounts_provider_user"),
    )

    op.add_column("payments", sa.Column("account_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_payments_account_id", "payments", "accounts", ["account_id"], ["id"]
    )
    op.create_index("ix_payments_account_id", "payments", ["account_id"])

    op.add_column("users", sa.Column("account_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_users_account_id", "users", "accounts", ["account_id"], ["id"])
    op.create_index("ix_users_account_id", "users", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_users_account_id", table_name="users")
    op.drop_constraint("fk_users_account_id", "users", type_="foreignkey")
    op.drop_column("users", "account_id")

    op.drop_index("ix_payments_account_id", table_name="payments")
    op.drop_constraint("fk_payments_account_id", "payments", type_="foreignkey")
    op.drop_column("payments", "account_id")

    op.drop_table("accounts")
