"""SocialLoginUseCase 핵심 분기 단위 테스트 (HM-BE-77 SC).

과거(비로그인) 결제 이메일 매칭 귀속은 의도적으로 제거됨 (무인증 /update-email
변조로 인한 타인 결제 탈취 경로 차단) — 관련 테스트 없음. 보관함 결제 연결은 P7에서
'로그인 후 결제' 경로(결제 시점 account_id 직접 연결)로 검증.

대상:
    1. 신규 로그인 — 계정 생성 + JWT 발급 + is_new_account=True
    2. 재로그인 — 계정 중복 생성 0, is_new_account=False, last_login_at 갱신
    3. 동시 첫 로그인 레이스 — UNIQUE 충돌 시 재조회→update 합류 (500 아님)
    4. 미지원 provider — UnsupportedProviderError
    5. 재로그인 닉네임 변경 — 프로필 최신화
    6. 이메일 동의 철회(None) 재로그인 — 기존 프로필 이메일 유지
    7. GetMeUseCase — last_used 유/무 응답 형태

Mock 전략: unittest.mock 대신 Port 직접 구현 fake.
"""

from datetime import date, time

import pytest

from app.domains.auth.application.request.social_login_request import SocialLoginRequest
from app.domains.auth.application.usecase.get_me_usecase import GetMeUseCase
from app.domains.auth.application.usecase.social_login_usecase import (
    SocialLoginUseCase,
    UnsupportedProviderError,
)
from app.domains.auth.domain.entity.account import Account
from app.domains.auth.domain.port.account_repository_port import (
    AccountAlreadyExistsError,
)
from app.domains.auth.domain.value_object.calendar_type import CalendarType
from app.domains.auth.domain.value_object.gender import Gender
from app.domains.auth.domain.value_object.last_used_profile import LastUsedProfile
from app.domains.auth.domain.value_object.oauth_profile import OAuthProfile
from app.domains.auth.domain.value_object.provider import Provider

# ── Test fakes ────────────────────────────────────────────────────────────────


class FakeOAuthClient:
    def __init__(self, profile: OAuthProfile) -> None:
        self.profile = profile
        self.calls: list[tuple[str, str]] = []

    async def fetch_profile(self, *, code: str, redirect_uri: str) -> OAuthProfile:
        self.calls.append((code, redirect_uri))
        return self.profile


class FakeAccountRepository:
    """In-memory 계정 저장소. (provider, provider_user_id) 자연키 upsert 흉내."""

    def __init__(self) -> None:
        self._by_id: dict[int, Account] = {}
        self._next_id = 1

    async def save(self, account: Account) -> Account:
        account.id = self._next_id
        self._next_id += 1
        self._by_id[account.id] = account
        return account

    async def update(self, account: Account) -> Account:
        assert account.id is not None
        self._by_id[account.id] = account
        return account

    async def find_by_id(self, account_id: int) -> Account | None:
        return self._by_id.get(account_id)

    async def find_by_provider_user(
        self, provider: Provider, provider_user_id: str
    ) -> Account | None:
        for acc in self._by_id.values():
            if acc.provider == provider and acc.provider_user_id == provider_user_id:
                return acc
        return None

    @property
    def count(self) -> int:
        return len(self._by_id)


class FakeTokenIssuer:
    def issue(self, account_id: int) -> str:
        return f"jwt-for-{account_id}"

    def decode(self, token: str) -> int:
        return int(token.removeprefix("jwt-for-"))


def _kakao_profile(
    *,
    email: str | None = "user@example.com",
    email_verified: bool = True,
    nickname: str | None = "깨비",
) -> OAuthProfile:
    return OAuthProfile(
        provider=Provider.KAKAO,
        provider_user_id="12345",
        email=email,
        email_verified=email_verified,
        nickname=nickname,
        profile_image_url=None,
    )


def _make_usecase(
    profile: OAuthProfile,
    *,
    repo: FakeAccountRepository | None = None,
) -> tuple[SocialLoginUseCase, FakeAccountRepository]:
    repo = repo or FakeAccountRepository()
    usecase = SocialLoginUseCase(
        oauth_clients={Provider.KAKAO: FakeOAuthClient(profile)},
        account_repo=repo,
        token_issuer=FakeTokenIssuer(),
    )
    return usecase, repo


_REQUEST = SocialLoginRequest(
    provider=Provider.KAKAO,
    code="auth-code",
    redirect_uri="http://localhost:3000/auth/callback/kakao/",
)


# ── Tests ─────────────────────────────────────────────────────────────────────


async def test_first_login_creates_account() -> None:
    usecase, repo = _make_usecase(_kakao_profile())
    response = await usecase.execute(_REQUEST)

    assert response.is_new_account is True
    assert response.access_token == "jwt-for-1"
    assert response.profile.nickname == "깨비"
    assert repo.count == 1


async def test_relogin_does_not_duplicate_account() -> None:
    usecase, repo = _make_usecase(_kakao_profile())
    first = await usecase.execute(_REQUEST)
    second = await usecase.execute(_REQUEST)

    assert repo.count == 1
    assert second.is_new_account is False
    assert second.access_token == first.access_token

    account = await repo.find_by_id(1)
    assert account is not None
    assert account.last_login_at is not None


async def test_concurrent_first_login_race_converges() -> None:
    """동시 첫 로그인: save가 UNIQUE 충돌(AccountAlreadyExistsError) 던져도
    재조회→update로 합류, 500 대신 기존 계정으로 수렴 (is_new_account=False)."""

    class RacingRepository(FakeAccountRepository):
        """첫 save 시점엔 빈 상태였다가, save 직전 다른 요청이 INSERT한 상황 재현."""

        def __init__(self) -> None:
            super().__init__()
            self._raced = False

        async def save(self, account: Account) -> Account:
            if not self._raced:
                self._raced = True
                # 승자가 먼저 만든 계정을 주입한 뒤 패자 save는 충돌로 거부
                winner = Account(
                    provider=account.provider,
                    provider_user_id=account.provider_user_id,
                    email=account.email,
                    email_verified=account.email_verified,
                    nickname="승자닉",
                )
                await super().save(winner)
                raise AccountAlreadyExistsError("uq 충돌")
            return await super().save(account)

    repo = RacingRepository()
    usecase, _ = _make_usecase(_kakao_profile(), repo=repo)
    response = await usecase.execute(_REQUEST)

    assert repo.count == 1  # 중복 생성 0
    assert response.is_new_account is False
    assert response.access_token == "jwt-for-1"


async def test_unsupported_provider_rejected() -> None:
    usecase, _ = _make_usecase(_kakao_profile())
    google_request = SocialLoginRequest(
        provider=Provider.GOOGLE,
        code="auth-code",
        redirect_uri="http://localhost:3000/auth/callback/google/",
    )
    with pytest.raises(UnsupportedProviderError):
        await usecase.execute(google_request)


async def test_relogin_refreshes_nickname() -> None:
    repo = FakeAccountRepository()
    usecase1, _ = _make_usecase(_kakao_profile(nickname="옛닉"), repo=repo)
    await usecase1.execute(_REQUEST)

    usecase2, _ = _make_usecase(_kakao_profile(nickname="새닉"), repo=repo)
    response = await usecase2.execute(_REQUEST)

    assert response.profile.nickname == "새닉"


async def test_email_withdrawal_keeps_existing_email() -> None:
    """동의 철회로 이메일이 안 내려와도 기존 프로필 이메일을 지우지 않는다."""
    repo = FakeAccountRepository()
    usecase1, _ = _make_usecase(_kakao_profile(), repo=repo)
    await usecase1.execute(_REQUEST)

    usecase2, _ = _make_usecase(
        _kakao_profile(email=None, email_verified=False), repo=repo
    )
    response = await usecase2.execute(_REQUEST)

    assert response.profile.email == "user@example.com"


async def test_get_me_with_and_without_last_used() -> None:
    repo = FakeAccountRepository()
    await repo.save(Account(provider=Provider.KAKAO, provider_user_id="1"))
    await repo.save(
        Account(
            provider=Provider.GOOGLE,
            provider_user_id="2",
            nickname="도윤",
            last_used=LastUsedProfile(
                name="홍길동",
                birth_date=date(1995, 3, 1),
                calendar_type=CalendarType.SOLAR,
                birth_time=time(11, 30),
                birth_time_unknown=False,
                gender=Gender.MALE,
            ),
        )
    )
    usecase = GetMeUseCase(account_repo=repo)

    without = await usecase.execute(1)
    assert without.last_used is None

    with_profile = await usecase.execute(2)
    assert with_profile.last_used is not None
    assert with_profile.last_used.name == "홍길동"
    assert with_profile.last_used.birth == "1995-03-01"
    assert with_profile.last_used.time == "11:30"
    assert with_profile.last_used.gender == "male"

    with pytest.raises(ValueError):
        await usecase.execute(999)
