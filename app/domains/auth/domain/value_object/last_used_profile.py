from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

from app.domains.auth.domain.value_object.calendar_type import CalendarType
from app.domains.auth.domain.value_object.gender import Gender


@dataclass(frozen=True)
class LastUsedProfile:
    """계정의 '마지막 사용' 사주 입력값 스냅샷.

    카카오/구글 = 계정 신원, 이 값 = 자가입력 사주정보 — 둘은 별개 데이터.
    사용자가 타인 정보를 입력할 수 있으므로 첫 입력이 아니라 항상 마지막 제출값을 기록,
    다음 설문에서 prefill로만 사용한다 (검증 책임은 제출 시점의 각 플로에 있음).
    """

    name: str
    birth_date: date
    calendar_type: CalendarType
    birth_time: time | None
    birth_time_unknown: bool
    gender: Gender
