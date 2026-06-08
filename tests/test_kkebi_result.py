"""깨비 결과 저장/조회 테스트 (HM-BE-79).

대상:
    1. 로그인(account_id) — 합성 후 save_today 호출(cycle_id/name/result 전달)
    2. 비로그인(account_id=None) — 저장 안 함 (기존 플로 불변)
    3. 저장 실패 — 비치명(운세 응답은 정상 반환)
    4. GetSavedDailyResultUseCase — 저장본 있으면 result 반환 / 없으면 ValueError
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from app.domains.kkebi.application.request.kkebi_fortune_request import KkebiFortuneRequest
from app.domains.kkebi.application.usecase.get_daily_fortune_usecase import (
    GetDailyFortuneUseCase,
)
from app.domains.kkebi.application.usecase.get_saved_daily_result_usecase import (
    GetSavedDailyResultUseCase,
)
from app.domains.kkebi.domain.entity.kkebi_result import KkebiResult
from app.domains.kkebi.domain.service.ganzhi_calendar import cycle_id
from tests.test_kkebi_usecase import FakeFortuneTeller, FakeRepo

_KST = timezone(timedelta(hours=9))


class FakeResultRepo:
    def __init__(self, *, fail: bool = False, existing: KkebiResult | None = None) -> None:
        self._fail = fail
        self._existing = existing
        self.saved: dict[str, Any] | None = None

    async def save_today(
        self, *, account_id: int, cycle_id: str, name: str, result: dict[str, Any]
    ) -> None:
        if self._fail:
            raise RuntimeError("DB down")
        self.saved = {
            "account_id": account_id,
            "cycle_id": cycle_id,
            "name": name,
            "result": result,
        }

    async def find_today(self, *, account_id: int, cycle_id: str) -> KkebiResult | None:
        return self._existing


def _req() -> KkebiFortuneRequest:
    return KkebiFortuneRequest(name="수아", birth="1998-03-15", hour=None, gender="F")


def _usecase(result_repo: FakeResultRepo | None) -> GetDailyFortuneUseCase:
    return GetDailyFortuneUseCase(
        fortuneteller=FakeFortuneTeller("갑", "자"),
        template_repo=FakeRepo(),
        result_repo=result_repo,
    )


async def test_logged_in_saves_result() -> None:
    repo = FakeResultRepo()
    usecase = _usecase(repo)
    resp = await usecase.execute(_req(), account_id=42)

    assert repo.saved is not None
    assert repo.saved["account_id"] == 42
    assert repo.saved["name"] == "수아"
    # cycle_id는 오늘(KST) — 응답 cycle.id와 동일
    assert repo.saved["cycle_id"] == resp.cycle.id == cycle_id(datetime.now(_KST).date())
    # result는 응답 직렬화본
    assert repo.saved["result"]["total"]["score"] == resp.total.score


async def test_anonymous_does_not_save() -> None:
    repo = FakeResultRepo()
    usecase = _usecase(repo)
    await usecase.execute(_req(), account_id=None)
    assert repo.saved is None


async def test_save_failure_is_non_fatal() -> None:
    repo = FakeResultRepo(fail=True)
    usecase = _usecase(repo)
    # 저장이 터져도 운세 응답은 정상 반환
    resp = await usecase.execute(_req(), account_id=42)
    assert resp.user.name == "수아"
    assert resp.total.score


async def test_get_saved_today_returns_result() -> None:
    today = cycle_id(datetime.now(_KST).date())
    # 실제 DailyFortuneResponse 직렬화본을 저장본으로 사용 (model_validate 라운드트립)
    generated = await _usecase(None).execute(_req())
    saved = KkebiResult(
        account_id=42, cycle_id=today, name="수아", result=generated.model_dump()
    )
    usecase = GetSavedDailyResultUseCase(result_repo=FakeResultRepo(existing=saved))
    out = await usecase.execute(42)
    assert out.total.score == generated.total.score
    assert out.user.name == "수아"


async def test_get_saved_today_404_when_none() -> None:
    usecase = GetSavedDailyResultUseCase(result_repo=FakeResultRepo(existing=None))
    with pytest.raises(ValueError):
        await usecase.execute(42)
