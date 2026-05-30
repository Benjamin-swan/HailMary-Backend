"""양력 날짜 → 오늘의 일진(60갑자) 계산 (순수 Python).

율리우스적일(JDN) 기반 표준 공식. FortuneTeller는 오늘 일진을 주지 않으므로
BE에서 직접 계산한다.

검증 기준일(교차검증):
- 2000-01-01 (양력) = 戊午일
- 2000-01-07 (양력) = 甲子일 (60갑자 시작)
"""
from __future__ import annotations

from datetime import date

# 천간 10 / 지지 12 (한자 — saju_rules 와 동일 표기)
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _jdn(d: date) -> int:
    """그레고리력 날짜 → 율리우스적일(정수)."""
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return (
        d.day
        + (153 * m + 2) // 5
        + 365 * y
        + y // 4
        - y // 100
        + y // 400
        - 32045
    )


def ganzhi_index(d: date) -> int:
    """그날의 60갑자 인덱스 (甲子=0 ~ 癸亥=59)."""
    return (_jdn(d) + 49) % 60


def day_ganzhi(d: date) -> tuple[str, str]:
    """그날의 일진 (천간, 지지) 한자 튜플. 예: (戊, 午)."""
    idx = ganzhi_index(d)
    return STEMS[idx % 10], BRANCHES[idx % 12]


def cycle_id(d: date) -> str:
    """프론트 cycle.id 형식 YYYYMMDD."""
    return d.strftime("%Y%m%d")
