"""UpdateLastUsedUseCase 단위 테스트 (HM-BE-78).

대상:
    1. 사주 플로(시각 HH:MM) — last_used 전체 갱신
    2. 시간 모름("unknown") — birth_time=None, unknown=True
    3. 깨비 플로(time=None) — name/birth/calendar/gender 갱신, 기존 시각 보존
    4. time=None인데 기존 last_used 없음 — birth_time None/unknown True
    5. 계정 없음 — ValueError
    6. 재갱신 — 마지막 값으로 덮어쓰기(첫 값 아님)
"""

from datetime import date, time

import pytest

from app.domains.auth.application.request.update_last_used_request import (
    UpdateLastUsedRequest,
)
from app.domains.auth.application.usecase.update_last_used_usecase import (
    UpdateLastUsedUseCase,
)
from app.domains.auth.domain.entity.account import Account
from app.domains.auth.domain.value_object.calendar_type import CalendarType
from app.domains.auth.domain.value_object.gender import Gender
from app.domains.auth.domain.value_object.last_used_profile import LastUsedProfile
from app.domains.auth.domain.value_object.provider import Provider


class FakeAccountRepository:
    def __init__(self, account: Account | None) -> None:
        self._account = account
        self.updated: Account | None = None

    async def save(self, account: Account) -> Account:  # noqa: D102 - 미사용
        raise NotImplementedError

    async def update(self, account: Account) -> Account:
        self.updated = account
        return account

    async def find_by_id(self, account_id: int) -> Account | None:
        return self._account

    async def find_by_provider_user(self, provider, provider_user_id):  # type: ignore[no-untyped-def]
        raise NotImplementedError


def _account(last_used: LastUsedProfile | None = None) -> Account:
    return Account(
        provider=Provider.KAKAO,
        provider_user_id="1",
        email="a@b.com",
        id=7,
        last_used=last_used,
    )


async def test_saju_flow_updates_full() -> None:
    repo = FakeAccountRepository(_account())
    usecase = UpdateLastUsedUseCase(account_repo=repo)
    await usecase.execute(
        7,
        UpdateLastUsedRequest(
            name="홍길동", birth="1995-03-15", calendar=CalendarType.SOLAR,
            gender=Gender.MALE, time="11:30",
        ),
    )
    lu = repo.updated.last_used  # type: ignore[union-attr]
    assert lu == LastUsedProfile(
        name="홍길동", birth_date=date(1995, 3, 15), calendar_type=CalendarType.SOLAR,
        birth_time=time(11, 30), birth_time_unknown=False, gender=Gender.MALE,
    )


async def test_time_unknown() -> None:
    repo = FakeAccountRepository(_account())
    usecase = UpdateLastUsedUseCase(account_repo=repo)
    await usecase.execute(
        7,
        UpdateLastUsedRequest(
            name="김", birth="2000-01-01", calendar=CalendarType.LUNAR,
            gender=Gender.FEMALE, time="unknown",
        ),
    )
    lu = repo.updated.last_used  # type: ignore[union-attr]
    assert lu.birth_time is None
    assert lu.birth_time_unknown is True


async def test_kkebi_flow_preserves_existing_time() -> None:
    existing = LastUsedProfile(
        name="옛이름", birth_date=date(1990, 5, 5), calendar_type=CalendarType.SOLAR,
        birth_time=time(9, 0), birth_time_unknown=False, gender=Gender.MALE,
    )
    repo = FakeAccountRepository(_account(existing))
    usecase = UpdateLastUsedUseCase(account_repo=repo)
    # 깨비 — time=None → 기존 09:00 시각 유지, 나머지 갱신
    await usecase.execute(
        7,
        UpdateLastUsedRequest(
            name="새이름", birth="1988-08-08", calendar=CalendarType.SOLAR,
            gender=Gender.FEMALE, time=None,
        ),
    )
    lu = repo.updated.last_used  # type: ignore[union-attr]
    assert lu.name == "새이름"
    assert lu.birth_date == date(1988, 8, 8)
    assert lu.gender == Gender.FEMALE
    assert lu.birth_time == time(9, 0)  # 보존
    assert lu.birth_time_unknown is False


async def test_kkebi_flow_no_prior_last_used() -> None:
    repo = FakeAccountRepository(_account(None))
    usecase = UpdateLastUsedUseCase(account_repo=repo)
    await usecase.execute(
        7,
        UpdateLastUsedRequest(
            name="첫", birth="2001-02-03", calendar=CalendarType.SOLAR,
            gender=Gender.MALE, time=None,
        ),
    )
    lu = repo.updated.last_used  # type: ignore[union-attr]
    assert lu.birth_time is None
    assert lu.birth_time_unknown is True


async def test_account_not_found() -> None:
    repo = FakeAccountRepository(None)
    usecase = UpdateLastUsedUseCase(account_repo=repo)
    with pytest.raises(ValueError):
        await usecase.execute(
            999,
            UpdateLastUsedRequest(
                name="x", birth="2000-01-01", calendar=CalendarType.SOLAR,
                gender=Gender.MALE, time=None,
            ),
        )
