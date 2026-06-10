from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, field_validator

from app.domains.auth.domain.value_object.calendar_type import CalendarType
from app.domains.auth.domain.value_object.gender import Gender


class UpdateLastUsedRequest(BaseModel):
    """계정 '마지막 사용' 사주 입력값 갱신 요청.

    name/birth/calendar/gender는 모든 설문이 공통으로 가지는 값 → 항상 갱신.
    time은 부분 갱신:
      - "HH:MM" : 정확 시각
      - "unknown": 시간 모름(명시) → last_birth_time=null, unknown=true
      - None     : 시간 정보 없는 플로(깨비 등) → 기존 시간 값 유지(건드리지 않음)
    """

    name: str
    birth: str  # "YYYY-MM-DD"
    calendar: CalendarType
    gender: Gender
    time: str | None = None  # "HH:MM" | "unknown" | None

    @field_validator("birth")
    @classmethod
    def validate_birth(cls, v: str) -> str:
        date.fromisoformat(v)
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str | None) -> str | None:
        if v is None or v == "unknown":
            return v
        time.fromisoformat(v)  # "HH:MM" 검증
        return v

    def birth_date(self) -> date:
        return date.fromisoformat(self.birth)
