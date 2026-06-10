from enum import Enum


# user 도메인 CalendarType과 값 동일 — 도메인 간 직접 import 금지 원칙으로 auth 자체 정의.
class CalendarType(str, Enum):
    SOLAR = "solar"
    LUNAR = "lunar"
