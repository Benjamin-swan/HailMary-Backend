from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domains.auth.domain.value_object.last_used_profile import LastUsedProfile
from app.domains.auth.domain.value_object.provider import Provider


@dataclass
class Account:
    """소셜 로그인 계정. (provider, provider_user_id)가 자연키.

    기존 users 테이블(무료사주 제출 단위)과 별개 — users/payments가
    account_id FK로 이 계정에 귀속된다.
    """

    provider: Provider
    provider_user_id: str
    email: str | None = None
    email_verified: bool = False
    nickname: str | None = None
    profile_image_url: str | None = None
    last_used: LastUsedProfile | None = None
    id: int | None = None
    created_at: datetime | None = None
    last_login_at: datetime | None = None

    def __repr__(self) -> str:
        # 개인정보 로그 금지 룰 — 이메일 마스킹
        masked_email = f"{self.email[0]}***" if self.email else None
        return f"Account(id={self.id}, provider={self.provider.value}, email={masked_email})"

    def __str__(self) -> str:
        return self.__repr__()
