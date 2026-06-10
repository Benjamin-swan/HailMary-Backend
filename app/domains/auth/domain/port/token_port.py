from typing import Protocol


class TokenDecodeError(Exception):
    """만료/위조/형식 오류로 계정 토큰을 해독할 수 없음."""


class TokenIssuerPort(Protocol):
    """계정 인증 토큰(JWT) 발급/검증 포트.

    기존 session_token(무료사주 세션, users.session_token)과 완전 별개 —
    이 토큰은 accounts.id만 식별한다.
    """

    def issue(self, account_id: int) -> str: ...
    def decode(self, token: str) -> int: ...
