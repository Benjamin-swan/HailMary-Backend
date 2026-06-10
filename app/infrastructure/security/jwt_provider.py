"""계정 인증 JWT 발급/검증.

기존 session_token(무료사주 세션, users.session_token)과 완전 별개 —
이 토큰은 소셜 로그인 계정(accounts.id)만 식별한다.

sub 클레임은 RFC 7519에 따라 문자열로 인코딩 (PyJWT 2.x strict).
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.domains.auth.domain.port.token_port import TokenDecodeError, TokenIssuerPort

_ALGORITHM = "HS256"


class JwtTokenProvider(TokenIssuerPort):
    def __init__(self, *, secret: str, expires_days: int = 30) -> None:
        if not secret:
            raise ValueError("JWT_SECRET이 설정되지 않았습니다.")
        self._secret = secret
        self._expires_days = expires_days

    def issue(self, account_id: int) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": str(account_id),
            "iat": now,
            "exp": now + timedelta(days=self._expires_days),
        }
        return jwt.encode(payload, self._secret, algorithm=_ALGORITHM)

    def decode(self, token: str) -> int:
        try:
            payload: dict[str, Any] = jwt.decode(
                token, self._secret, algorithms=[_ALGORITHM]
            )
        except jwt.InvalidTokenError as e:  # ExpiredSignatureError 포함 상위 타입
            raise TokenDecodeError(str(e)) from e
        try:
            return int(payload["sub"])
        except (KeyError, TypeError, ValueError) as e:
            raise TokenDecodeError("sub 클레임이 계정 ID 형식이 아닙니다") from e
