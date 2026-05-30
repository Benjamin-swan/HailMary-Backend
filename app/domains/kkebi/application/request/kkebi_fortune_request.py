from __future__ import annotations

from datetime import date

from pydantic import BaseModel, field_validator

# 프론트 gender(M/F/X) → 도메인 Gender enum value
GENDER_MAP = {"M": "male", "F": "female", "X": "other"}


class KkebiFortuneRequest(BaseModel):
    """프론트 입력 폼 → 깨비 일일사주 요청.

    프론트가 쿠키에서 읽어 보내는 형식:
      name: str
      birth: "YYYY-MM-DD" (양력)
      hour: 0~11 (시진 인덱스) | None (모름)  ← 일일운세는 일주만 쓰므로 미사용
      gender: "M" | "F" | "X"
    """
    name: str
    birth: str
    hour: int | None = None
    gender: str

    @field_validator("birth")
    @classmethod
    def _validate_birth(cls, v: str) -> str:
        date.fromisoformat(v)
        return v

    @field_validator("gender")
    @classmethod
    def _validate_gender(cls, v: str) -> str:
        if v not in GENDER_MAP:
            raise ValueError(f"gender must be one of {list(GENDER_MAP)}")
        return v

    def birth_date(self) -> date:
        return date.fromisoformat(self.birth)

    def gender_value(self) -> str:
        return GENDER_MAP[self.gender]
