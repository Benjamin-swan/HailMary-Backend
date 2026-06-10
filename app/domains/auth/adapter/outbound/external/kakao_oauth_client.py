"""카카오 OAuth 클라이언트 (REST API 방식).

토큰 교환: POST {auth_base}/oauth/token  (form-urlencoded)
프로필:    GET  {api_base}/v2/user/me     (Bearer access_token)

이메일은 비즈 앱 동의항목(account_email) 기준 — is_email_valid && is_email_verified
둘 다 참일 때만 검증된 이메일로 취급한다 (결제 귀속 안전 조건).
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


class KakaoOAuthClient(OAuthClientPort):
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        auth_base_url: str = "https://kauth.kakao.com",
        api_base_url: str = "https://kapi.kakao.com",
        verify_tls: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """verify_tls — Windows 로컬에서 asyncmy 동봉 OpenSSL 충돌(OPENSSL_Uplink)로
        SSLContext 생성이 크래시함 → main.py가 local 환경에서만 False 주입 (PayApp 선례).
        transport — 테스트용 httpx.MockTransport 주입 지점 (SSL 비접촉).
        """
        if not client_id or not client_secret:
            raise ValueError("카카오 OAuth 설정(client_id/client_secret)이 비어 있습니다.")
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_base_url = auth_base_url.rstrip("/")
        self._api_base_url = api_base_url.rstrip("/")
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
                    f"{self._auth_base_url}/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                    },
                )
            except httpx.RequestError as e:
                raise OAuthExchangeError(f"카카오 토큰 교환 연결 실패: {e}") from e
            if token_resp.status_code != 200:
                # 본문에 error_description이 오지만 code 원문이 섞일 수 있어 코드만 남김
                error_code = token_resp.json().get("error_code", "unknown") if _is_json(token_resp) else "unknown"
                raise OAuthExchangeError(
                    f"카카오 토큰 교환 실패 (HTTP {token_resp.status_code}, {error_code})"
                )
            access_token = token_resp.json().get("access_token")
            if not access_token:
                raise OAuthExchangeError("카카오 토큰 응답에 access_token이 없습니다")

            try:
                me_resp = await client.get(
                    f"{self._api_base_url}/v2/user/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            except httpx.RequestError as e:
                raise OAuthExchangeError(f"카카오 프로필 조회 연결 실패: {e}") from e
            if me_resp.status_code != 200:
                raise OAuthExchangeError(f"카카오 프로필 조회 실패 (HTTP {me_resp.status_code})")
            data: dict[str, Any] = me_resp.json()

        provider_user_id = data.get("id")
        if provider_user_id is None:
            raise OAuthExchangeError("카카오 프로필 응답에 id가 없습니다")

        kakao_account: dict[str, Any] = data.get("kakao_account") or {}
        kakao_profile: dict[str, Any] = kakao_account.get("profile") or {}
        email: str | None = kakao_account.get("email")
        email_verified = bool(
            email
            and kakao_account.get("is_email_valid")
            and kakao_account.get("is_email_verified")
        )
        return OAuthProfile(
            provider=Provider.KAKAO,
            provider_user_id=str(provider_user_id),
            email=email,
            email_verified=email_verified,
            nickname=kakao_profile.get("nickname"),
            profile_image_url=kakao_profile.get("thumbnail_image_url"),
        )


def _is_json(resp: httpx.Response) -> bool:
    content_type: str = resp.headers.get("content-type", "")
    return content_type.startswith("application/json")
