"""카카오/구글 OAuth 클라이언트 응답 파싱 테스트.

Mock 전략: httpx.MockTransport 주입 — pytest-httpx는 실제 HTTPTransport를 패치하는
방식이라 Windows 로컬의 OPENSSL_Uplink 크래시(asyncmy 동봉 OpenSSL 충돌)를 피할 수
없다. MockTransport는 SSLContext를 아예 만들지 않아 크로스 플랫폼 안전.

대상:
    1. 카카오 정상 — id/email/검증 플래그/닉네임 파싱 + 교환 요청 form 필드
    2. 카카오 이메일 미검증 — email_verified=False
    3. 카카오 토큰 교환 실패(400) — OAuthExchangeError
    4. 구글 정상 — sub/email_verified/name/picture 파싱
    5. 구글 프로필 조회 실패(401) — OAuthExchangeError
    6. 빈 키 — 생성 거부 (ValueError)
"""

from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest

from app.domains.auth.adapter.outbound.external.google_oauth_client import (
    GoogleOAuthClient,
)
from app.domains.auth.adapter.outbound.external.kakao_oauth_client import (
    KakaoOAuthClient,
)
from app.domains.auth.domain.port.oauth_client_port import OAuthExchangeError
from app.domains.auth.domain.value_object.provider import Provider

_KAKAO_REDIRECT = "http://localhost:3000/auth/callback/kakao/"
_GOOGLE_REDIRECT = "http://localhost:3000/auth/callback/google/"


def _make_transport(
    routes: dict[tuple[str, str], httpx.Response],
    captured: list[httpx.Request] | None = None,
) -> httpx.MockTransport:
    """(METHOD, url) → 응답 매핑 transport. captured에 요청 원문 수집."""

    def handler(request: httpx.Request) -> httpx.Response:
        if captured is not None:
            captured.append(request)
        key = (request.method, str(request.url))
        if key not in routes:
            raise AssertionError(f"예상 밖 요청: {key}")
        return routes[key]

    return httpx.MockTransport(handler)


def _kakao_client(
    routes: dict[tuple[str, str], httpx.Response],
    captured: list[httpx.Request] | None = None,
) -> KakaoOAuthClient:
    return KakaoOAuthClient(
        client_id="kid",
        client_secret="ksecret",
        transport=_make_transport(routes, captured),
    )


def _google_client(
    routes: dict[tuple[str, str], httpx.Response],
) -> GoogleOAuthClient:
    return GoogleOAuthClient(
        client_id="gid",
        client_secret="gsecret",
        transport=_make_transport(routes),
    )


def _json(payload: dict[str, Any], status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=payload)


async def test_kakao_parses_profile() -> None:
    captured: list[httpx.Request] = []
    client = _kakao_client(
        {
            ("POST", "https://kauth.kakao.com/oauth/token"): _json(
                {"access_token": "kakao-at", "token_type": "bearer"}
            ),
            ("GET", "https://kapi.kakao.com/v2/user/me"): _json(
                {
                    "id": 998877,
                    "kakao_account": {
                        "email": "kkebi@example.com",
                        "is_email_valid": True,
                        "is_email_verified": True,
                        "profile": {
                            "nickname": "깨비",
                            "thumbnail_image_url": "http://img",
                        },
                    },
                }
            ),
        },
        captured,
    )
    profile = await client.fetch_profile(code="c", redirect_uri=_KAKAO_REDIRECT)

    assert profile.provider == Provider.KAKAO
    assert profile.provider_user_id == "998877"
    assert profile.email == "kkebi@example.com"
    assert profile.email_verified is True
    assert profile.nickname == "깨비"
    assert profile.profile_image_url == "http://img"

    # 토큰 교환 요청 form 필드 검증 (redirect_uri가 그대로 전달돼야 제공자 검증 통과)
    token_request = captured[0]
    form = parse_qs(token_request.content.decode())
    assert form["grant_type"] == ["authorization_code"]
    assert form["client_id"] == ["kid"]
    assert form["redirect_uri"] == [_KAKAO_REDIRECT]
    assert form["code"] == ["c"]


async def test_kakao_unverified_email() -> None:
    client = _kakao_client(
        {
            ("POST", "https://kauth.kakao.com/oauth/token"): _json(
                {"access_token": "kakao-at"}
            ),
            ("GET", "https://kapi.kakao.com/v2/user/me"): _json(
                {
                    "id": 1,
                    "kakao_account": {
                        "email": "kkebi@example.com",
                        "is_email_valid": True,
                        "is_email_verified": False,
                        "profile": {"nickname": "깨비"},
                    },
                }
            ),
        }
    )
    profile = await client.fetch_profile(code="c", redirect_uri=_KAKAO_REDIRECT)

    assert profile.email == "kkebi@example.com"
    assert profile.email_verified is False


async def test_kakao_token_exchange_failure() -> None:
    client = _kakao_client(
        {
            ("POST", "https://kauth.kakao.com/oauth/token"): _json(
                {"error": "invalid_grant", "error_code": "KOE320"}, status_code=400
            ),
        }
    )
    with pytest.raises(OAuthExchangeError):
        await client.fetch_profile(code="expired", redirect_uri=_KAKAO_REDIRECT)


async def test_google_parses_profile() -> None:
    client = _google_client(
        {
            ("POST", "https://oauth2.googleapis.com/token"): _json(
                {"access_token": "google-at"}
            ),
            ("GET", "https://openidconnect.googleapis.com/v1/userinfo"): _json(
                {
                    "sub": "10769150350006150715113082367",
                    "email": "doyoon@gmail.com",
                    "email_verified": True,
                    "name": "한도윤",
                    "picture": "http://pic",
                }
            ),
        }
    )
    profile = await client.fetch_profile(code="c", redirect_uri=_GOOGLE_REDIRECT)

    assert profile.provider == Provider.GOOGLE
    assert profile.provider_user_id == "10769150350006150715113082367"
    assert profile.email == "doyoon@gmail.com"
    assert profile.email_verified is True
    assert profile.nickname == "한도윤"
    assert profile.profile_image_url == "http://pic"


async def test_google_userinfo_failure() -> None:
    client = _google_client(
        {
            ("POST", "https://oauth2.googleapis.com/token"): _json(
                {"access_token": "google-at"}
            ),
            ("GET", "https://openidconnect.googleapis.com/v1/userinfo"): _json(
                {"error": "invalid_token"}, status_code=401
            ),
        }
    )
    with pytest.raises(OAuthExchangeError):
        await client.fetch_profile(code="c", redirect_uri=_GOOGLE_REDIRECT)


def test_empty_credentials_rejected() -> None:
    with pytest.raises(ValueError):
        KakaoOAuthClient(client_id="", client_secret="x")
    with pytest.raises(ValueError):
        GoogleOAuthClient(client_id="x", client_secret="")
