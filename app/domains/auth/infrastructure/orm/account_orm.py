from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, Enum, String, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.auth.domain.value_object.calendar_type import CalendarType
from app.domains.auth.domain.value_object.gender import Gender
from app.domains.auth.domain.value_object.provider import Provider
from app.infrastructure.database.session import Base


class AccountORM(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_accounts_provider_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[Provider] = mapped_column(
        Enum(Provider, values_callable=lambda e: [x.value for x in e]), nullable=False
    )
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # ── 마지막 사용 사주 입력값 (설문 prefill용 스냅샷, P5에서 갱신 배선) ──
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_calendar_type: Mapped[CalendarType | None] = mapped_column(
        Enum(CalendarType, values_callable=lambda e: [x.value for x in e]), nullable=True
    )
    last_birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    last_birth_time_unknown: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    last_gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, values_callable=lambda e: [x.value for x in e]), nullable=True
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
