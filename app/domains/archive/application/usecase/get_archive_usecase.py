from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

from app.domains.archive.application.response.archive_response import (
    ArchiveResponse,
    KkebiArchiveItem,
    PaidArchiveItem,
)
from app.domains.archive.domain.port.archive_repository_port import (
    ArchiveRepositoryPort,
)
from app.domains.kkebi.domain.service.ganzhi_calendar import cycle_id

_KST = timezone(timedelta(hours=9))


def _as_utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt


class GetArchiveUseCase:
    """보관함 — 계정 귀속 결제 결과 목록 + 깨비 당일 저장 여부."""

    def __init__(self, *, archive_repo: ArchiveRepositoryPort) -> None:
        self._archive_repo = archive_repo

    async def execute(self, account_id: int) -> ArchiveResponse:
        now = datetime.now(UTC)
        paid_rows = await self._archive_repo.list_paid(account_id)
        # 만료된 결과지는 보관함에서 제외 — 재결제 유도 대신 깔끔히 비운다(2026-06-08 결정).
        # (재구매해도 사주 결과는 거의 동일 → 재결제 전환 낮고 클러터만 증가)
        # MySQL DATETIME은 naive 로드 → UTC 부여 후 비교 (get_paid_report_usecase 동일 패턴)
        paid = [
            PaidArchiveItem(
                character=r.character,
                orderId=r.order_id,
                shareCode=r.share_code,
                approvedAt=r.approved_at,
                expiresAt=r.expires_at,
            )
            for r in paid_rows
            if now < _as_utc(r.expires_at)
        ]

        today = cycle_id(datetime.now(_KST).date())
        kkebi_row = await self._archive_repo.find_kkebi_today(account_id, today)
        kkebi = (
            KkebiArchiveItem(cycleId=kkebi_row.cycle_id, summary=kkebi_row.summary)
            if kkebi_row is not None
            else None
        )

        return ArchiveResponse(paid=paid, kkebi=kkebi)
