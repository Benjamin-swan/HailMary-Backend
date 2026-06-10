"""보관함 집계 조회 — 여러 도메인 테이블을 읽는 read-only 어댑터.

payments(account 귀속, DONE) × paid_reports(share_code) 조인 + kkebi_results 당일 조회.
쓰기 없음 — 각 도메인의 쓰기는 해당 도메인 리포지토리가 담당.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.ai.infrastructure.orm.paid_report_orm import PaidReportORM
from app.domains.archive.domain.port.archive_repository_port import (
    ArchiveRepositoryPort,
)
from app.domains.archive.domain.value_object.archive_rows import (
    KkebiArchiveRow,
    PaidArchiveRow,
)
from app.domains.kkebi.infrastructure.orm.kkebi_result_orm import KkebiResultORM
from app.domains.payment.domain.value_object.payment_status import PaymentStatus
from app.domains.payment.infrastructure.orm.payment_orm import PaymentORM


class ArchiveRepository(ArchiveRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_paid(self, account_id: int) -> list[PaidArchiveRow]:
        stmt = (
            select(PaymentORM, PaidReportORM.share_code)
            .outerjoin(
                PaidReportORM, PaymentORM.order_id == PaidReportORM.order_id
            )
            .where(
                PaymentORM.account_id == account_id,
                PaymentORM.status == PaymentStatus.DONE,
            )
            .order_by(PaymentORM.approved_at.desc())
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            PaidArchiveRow(
                character=payment.character.value,
                order_id=payment.order_id,
                share_code=share_code,
                approved_at=payment.approved_at,
                expires_at=payment.expires_at,
            )
            for payment, share_code in rows
        ]

    async def find_kkebi_today(
        self, account_id: int, cycle_id: str
    ) -> KkebiArchiveRow | None:
        orm = (
            await self._session.execute(
                select(KkebiResultORM).where(
                    KkebiResultORM.account_id == account_id,
                    KkebiResultORM.cycle_id == cycle_id,
                )
            )
        ).scalar_one_or_none()
        if orm is None:
            return None
        return KkebiArchiveRow(cycle_id=orm.cycle_id, summary=_extract_summary(orm.result))


def _extract_summary(result: dict[str, Any]) -> str | None:
    total = result.get("total") if isinstance(result, dict) else None
    if isinstance(total, dict):
        summary = total.get("summary")
        if isinstance(summary, str):
            return summary
    return None
