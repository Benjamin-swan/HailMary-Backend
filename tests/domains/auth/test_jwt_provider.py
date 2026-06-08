"""JwtTokenProvider 단위 테스트.

대상:
    1. issue→decode 왕복 — account_id 보존
    2. 만료 토큰 → TokenDecodeError
    3. 위조(다른 시크릿 서명) 토큰 → TokenDecodeError
    4. 형식 오류 문자열 → TokenDecodeError
    5. sub가 숫자가 아닌 토큰 → TokenDecodeError
    6. 빈 시크릿 → 생성 자체 거부 (ValueError)
"""

import jwt as pyjwt
import pytest

from app.domains.auth.domain.port.token_port import TokenDecodeError
from app.infrastructure.security.jwt_provider import JwtTokenProvider

# PyJWT 2.13+: HS256 키 32바이트 미만이면 InsecureKeyLengthWarning — 테스트도 충분히 길게.
_SECRET = "test-secret-for-jwt-provider-0123456789abcdef"
_OTHER_SECRET = "other-secret-for-jwt-provider-0123456789abcdef"


def test_issue_decode_roundtrip() -> None:
    provider = JwtTokenProvider(secret=_SECRET, expires_days=30)
    token = provider.issue(42)
    assert provider.decode(token) == 42


def test_expired_token_rejected() -> None:
    provider = JwtTokenProvider(secret=_SECRET, expires_days=-1)  # 발급 즉시 만료
    token = provider.issue(1)
    fresh = JwtTokenProvider(secret=_SECRET, expires_days=30)
    with pytest.raises(TokenDecodeError):
        fresh.decode(token)


def test_tampered_secret_rejected() -> None:
    other = JwtTokenProvider(secret=_OTHER_SECRET, expires_days=30)
    token = other.issue(1)
    provider = JwtTokenProvider(secret=_SECRET, expires_days=30)
    with pytest.raises(TokenDecodeError):
        provider.decode(token)


def test_malformed_token_rejected() -> None:
    provider = JwtTokenProvider(secret=_SECRET, expires_days=30)
    with pytest.raises(TokenDecodeError):
        provider.decode("not-a-jwt")


def test_non_numeric_sub_rejected() -> None:
    token = pyjwt.encode({"sub": "abc"}, _SECRET, algorithm="HS256")
    provider = JwtTokenProvider(secret=_SECRET, expires_days=30)
    with pytest.raises(TokenDecodeError):
        provider.decode(token)


def test_empty_secret_rejected() -> None:
    with pytest.raises(ValueError):
        JwtTokenProvider(secret="", expires_days=30)
