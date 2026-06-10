from typing import Protocol

from app.domains.auth.domain.value_object.oauth_profile import OAuthProfile


class OAuthExchangeError(Exception):
    """소셜 제공자와의 code→토큰 교환 또는 프로필 조회 실패."""


class OAuthClientPort(Protocol):
    """Authorization Code를 받아 제공자 프로필로 교환하는 포트.

    FE가 /auth/callback/{provider}/ 에서 받은 code와, 인가 요청에 사용했던
    redirect_uri를 그대로 전달한다 (제공자가 양쪽 일치 여부를 검증).
    """

    async def fetch_profile(self, *, code: str, redirect_uri: str) -> OAuthProfile: ...
