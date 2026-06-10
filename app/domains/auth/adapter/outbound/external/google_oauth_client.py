"""구글 OAuth 클라이언트 (Authorization Code 방식).

토큰 교환: POST {token_base}/token              (form-urlencoded)
프로필:    GET  {userinfo_base}/v1/userinfo     (Bearer access_token)

id_token 서명 검증 대신 userinfo 엔드포인트를 사용 — 우리 서버가 구글에 직접
HTTPS로 조회하므로 응답 자체가 신뢰 가능하고, 구글 공개키 캐싱 관리가 불필요.
구글 이메일은 email_verified 플래그를 그대로 따른다.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.domains.auth.domain.port.oauth_client_port import (
    OAuthClientPort,
    OAuthExchangeError,
)
from app.domains.auth.domain.value_object.oauth_profile import OAuthProfile
from app.domains.auth.domain.value_object.provider import Provider

_TIMEOUT_SECONDS = 15.0


class GoogleOAuthClient(OAuthClientPort):
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        token_base_url: str = "https://oauth2.googleapis.com",
        userinfo_base_url: str = "https://openidconnect.googleapis.com",
        verify_tls: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """verify_tls/transport — kakao_oauth_client와 동일한 Windows 로컬 SSL 크래시 회피 지점."""
        if not client_id or not client_secret:
            raise ValueError("구글 OAuth 설정(client_id/client_secret)이 비어 있습니다.")
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_base_url = token_base_url.rstrip("/")
        self._userinfo_base_url = userinfo_base_url.rstrip("/")
        self._verify_tls = verify_tls
        self._transport = transport

    def _make_client(self) -> httpx.AsyncClient:
        if self._transport is not None:
            return httpx.AsyncClient(timeout=_TIMEOUT_SECONDS, transport=self._transport)
        return httpx.AsyncClient(timeout=_TIMEOUT_SECONDS, verify=self._verify_tls)

    async def fetch_profile(self, *, code: str, redirect_uri: str) -> OAuthProfile:
        async with self._make_client() as client:
            try:
                token_resp = await client.post(
                    f"{self._token_base_url}/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                    },
                )
            except httpx.RequestError as e:
                raise OAuthExchangeError(f"구글 토큰 교환 연결 실패: {e}") from e
            if token_resp.status_code != 200:
                error = token_resp.json().get("error", "unknown") if _is_json(token_resp) else "unknown"
                raise OAuthExchangeError(
                    f"구글 토큰 교환 실패 (HTTP {token_resp.status_code}, {error})"
                )
            access_token = token_resp.json().get("access_token")
            if not access_token:
                raise OAuthExchangeError("구글 토큰 응답에 access_token이 없습니다")

            try:
                userinfo_resp = await client.get(
                    f"{self._userinfo_base_url}/v1/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            except httpx.RequestError as e:
                raise OAuthExchangeError(f"구글 프로필 조회 연결 실패: {e}") from e
            if userinfo_resp.status_code != 200:
                raise OAuthExchangeError(
                    f"구글 프로필 조회 실패 (HTTP {userinfo_resp.status_code})"
                )
            data: dict[str, Any] = userinfo_resp.json()

        sub = data.get("sub")
        if not sub:
            raise OAuthExchangeError("구글 프로필 응답에 sub가 없습니다")

        email: str | None = data.get("email")
        return OAuthProfile(
            provider=Provider.GOOGLE,
            provider_user_id=str(sub),
            email=email,
            email_verified=bool(email and data.get("email_verified")),
            nickname=data.get("name"),
            profile_image_url=data.get("picture"),
        )


def _is_json(resp: httpx.Response) -> bool:
    content_type: str = resp.headers.get("content-type", "")
    return content_type.startswith("application/json")
