"""GetArchiveUseCase 단위 테스트 (HM-BE-80).

대상:
    1. 결제 목록 매핑 + 만료 플래그(now 기준)
    2. share_code None(결과지 미합성) 통과
    3. 깨비 당일 저장본 있음 → kkebi 채움 / 없음 → None
    4. 빈 보관함
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

from app.domains.archive.application.usecase.get_archive_usecase import (
    GetArchiveUseCase,
)
from app.domains.archive.domain.value_object.archive_rows import (
    KkebiArchiveRow,
    PaidArchiveRow,
)
from app.domains.kkebi.domain.service.ganzhi_calendar import cycle_id

_KST = timezone(timedelta(hours=9))


class FakeArchiveRepo:
    def __init__(
        self,
        *,
        paid: list[PaidArchiveRow] | None = None,
        kkebi: KkebiArchiveRow | None = None,
    ) -> None:
        self._paid = paid or []
        self._kkebi = kkebi
        self.kkebi_query_cycle: str | None = None

    async def list_paid(self, account_id: int) -> list[PaidArchiveRow]:
        return self._paid

    async def find_kkebi_today(
        self, account_id: int, cycle_id: str
    ) -> KkebiArchiveRow | None:
        self.kkebi_query_cycle = cycle_id
        return self._kkebi


def _row(*, character: str, expires_in_days: int, share_code: str | None) -> PaidArchiveRow:
    now = datetime.now(UTC)
    return PaidArchiveRow(
        character=character,
        order_id=f"order_{character}",
        share_code=share_code,
        approved_at=now - timedelta(days=30 - expires_in_days),
        expires_at=now + timedelta(days=expires_in_days),
    )


async def test_expired_items_excluded() -> None:
    repo = FakeArchiveRepo(
        paid=[
            _row(character="yeonwoo", expires_in_days=10, share_code="abc"),
            _row(character="doyoon", expires_in_days=-1, share_code="def"),  # 만료 → 제외
        ]
    )
    resp = await GetArchiveUseCase(archive_repo=repo).execute(7)

    # 만료 건은 보관함에서 빠지고 활성 1건만
    assert len(resp.paid) == 1
    assert resp.paid[0].character == "yeonwoo"
    assert resp.paid[0].shareCode == "abc"


async def test_share_code_none_passes_through() -> None:
    repo = FakeArchiveRepo(
        paid=[_row(character="yeonwoo", expires_in_days=5, share_code=None)]
    )
    resp = await GetArchiveUseCase(archive_repo=repo).execute(7)
    assert resp.paid[0].shareCode is None


async def test_kkebi_present_and_cycle_is_today() -> None:
    repo = FakeArchiveRepo(kkebi=KkebiArchiveRow(cycle_id="20260608", summary="오늘 좋음"))
    resp = await GetArchiveUseCase(archive_repo=repo).execute(7)
    assert resp.kkebi is not None
    assert resp.kkebi.summary == "오늘 좋음"
    # 오늘(KST) cycle로 조회했는지
    assert repo.kkebi_query_cycle == cycle_id(datetime.now(_KST).date())


async def test_empty_archive() -> None:
    resp = await GetArchiveUseCase(archive_repo=FakeArchiveRepo()).execute(7)
    assert resp.paid == []
    assert resp.kkebi is None
