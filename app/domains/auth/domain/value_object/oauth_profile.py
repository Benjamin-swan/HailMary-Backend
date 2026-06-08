from __future__ import annotations

from dataclasses import dataclass

from app.domains.auth.domain.value_object.provider import Provider


@dataclass(frozen=True)
class OAuthProfile:
    """소셜 제공자(카카오/구글)에서 받아온 프로필 스냅샷.

    email_verified — 제공자가 이메일 소유를 검증했는지 여부.
    과거 결제 자동 귀속(backfill)은 검증된 이메일에서만 수행한다 (타인 결제 탈취 방지).
    """

    provider: Provider
    provider_user_id: str
    email: str | None
    email_verified: bool
    nickname: str | None
    profile_image_url: str | None
