from __future__ import annotations

from pydantic import BaseModel

from app.domains.auth.domain.entity.account import Account


class LastUsedProfileResponse(BaseModel):
    """설문 prefill용 마지막 사용값 — SubmitUserInfoRequest와 동일한 와이어 포맷."""

    name: str
    birth: str                # "YYYY-MM-DD"
    calendar: str             # "solar" | "lunar"
    time: str | None          # "HH:MM" 또는 null(모름)
    gender: str               # "male" | "female"


class AccountProfileResponse(BaseModel):
    provider: str
    email: str | None
    nickname: str | None
    profile_image_url: str | None
    last_used: LastUsedProfileResponse | None

    @classmethod
    def from_account(cls, account: Account) -> AccountProfileResponse:
        last_used: LastUsedProfileResponse | None = None
        if account.last_used is not None:
            lu = account.last_used
            time_str = (
                None
                if lu.birth_time_unknown or lu.birth_time is None
                else lu.birth_time.strftime("%H:%M")
            )
            last_used = LastUsedProfileResponse(
                name=lu.name,
                birth=lu.birth_date.isoformat(),
                calendar=lu.calendar_type.value,
                time=time_str,
                gender=lu.gender.value,
            )
        return cls(
            provider=account.provider.value,
            email=account.email,
            nickname=account.nickname,
            profile_image_url=account.profile_image_url,
            last_used=last_used,
        )
