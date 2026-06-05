from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.payment.domain.value_object.coupon_status import CouponStatus
from app.infrastructure.database.session import Base


class CouponORM(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    status: Mapped[CouponStatus] = mapped_column(
        Enum(CouponStatus, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    memo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    used_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
