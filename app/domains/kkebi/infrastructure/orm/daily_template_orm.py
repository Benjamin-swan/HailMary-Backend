from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class DailyTemplateORM(Base):
    __tablename__ = "daily_templates"
    __table_args__ = (
        UniqueConstraint("sipseong", "branch_rel", name="uq_daily_template_keys"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sipseong: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    branch_rel: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    body: Mapped[dict] = mapped_column(JSON, nullable=False)  # type: ignore[type-arg]
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, server_default=func.now()
    )
