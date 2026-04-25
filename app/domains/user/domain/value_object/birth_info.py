from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

from app.domains.user.domain.value_object.calendar_type import CalendarType


@dataclass(frozen=True)
class BirthInfo:
    birth_date: date
    calendar_type: CalendarType
    birth_time: time | None = None
    birth_time_unknown: bool = False

    def __post_init__(self) -> None:
        if self.birth_time is not None and self.birth_time_unknown:
            raise ValueError("birth_time과 birth_time_unknown을 동시에 설정할 수 없습니다.")

    def birth_time_str(self) -> str | None:
        """FortuneTeller 전송용 문자열. 모르면 None."""
        if self.birth_time_unknown or self.birth_time is None:
            return None
        return self.birth_time.strftime("%H:%M")

    def __repr__(self) -> str:
        return f"BirthInfo(calendar={self.calendar_type.value}, unknown_time={self.birth_time_unknown})"
