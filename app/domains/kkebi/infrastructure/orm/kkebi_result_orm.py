from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class KkebiResultORM(Base):
    __tablename__ = "kkebi_results"
    __table_args__ = (
        UniqueConstraint("account_id", "cycle_id", name="uq_kkebi_results_account_cycle"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False, index=True
    )
    cycle_id: Mapped[str] = mapped_column(String(8), nullable=False)  # KST YYYYMMDD
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, server_default=func.now()
    )
