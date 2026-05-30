"""행운 요소(색/숫자/방위/음식) 룰 (순수 Python).

프론트 SajuResult.lucky 는 슬롯(AI 본문)에 없으므로 룰로 산출.

설계: (오늘 일진 간지 + 사용자 일주 간지)를 해시해 4요소를 뽑는다.
- 5영역 점수가 (오늘×사용자)로 매일·매인 다른 것과 동일 철학.
- 같은 사람·같은 날 → 항상 같음(결정론적, 하루 안 일관 / 캐시·재현 안전).
- 같은 사람·다른 날 → 다름. 같은 날·다른 사람 → 다름.
행운요소는 엄격한 명리 규칙이 없는 재미 영역이라 결정론적 해시 변주가 합리적.
Math.random/Date 미사용(순수 함수).
"""
from __future__ import annotations

import hashlib
from typing import TypedDict


class ColorDict(TypedDict):
    hex: str
    name: str


class FoodDict(TypedDict):
    name: str


class LuckyDict(TypedDict):
    color: ColorDict
    number: int
    direction: str
    food: FoodDict


# 색 풀 (이름 + hex)
_COLORS: list[ColorDict] = [
    {"hex": "#E85D52", "name": "코랄"},
    {"hex": "#4CAF50", "name": "초록"},
    {"hex": "#2D6CDF", "name": "블루"},
    {"hex": "#F2C94C", "name": "노랑"},
    {"hex": "#E0C068", "name": "골드"},
    {"hex": "#9B6BCC", "name": "보라"},
    {"hex": "#FF8FB1", "name": "핑크"},
    {"hex": "#5BC0BE", "name": "민트"},
    {"hex": "#FF9F45", "name": "주황"},
    {"hex": "#F5F0E6", "name": "아이보리"},
]

# 방위 풀 (프론트 허용 8방위)
_DIRECTIONS: list[str] = ["東", "西", "南", "北", "東北", "西北", "東南", "西南"]

# 음식 풀
_FOODS: list[str] = [
    "비빔밥", "떡볶이", "미역국", "단호박죽", "두부김치",
    "김밥", "불고기", "잡채", "콩나물국밥", "약과",
    "수정과", "호떡", "전복죽", "갈비탕", "약식",
]


def _seed(today_stem: str, today_branch: str, user_stem: str, user_branch: str) -> int:
    """오늘 일진 + 사용자 일주 → 안정적 정수 시드 (sha1 기반)."""
    key = f"{today_stem}{today_branch}|{user_stem}{user_branch}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return int(digest, 16)


def lucky_for(
    today_stem: str,
    today_branch: str,
    user_stem: str,
    user_branch: str,
) -> LuckyDict:
    """오늘 일진 × 사용자 일주 → lucky dict (매일·매인 다르게, 결정론적)."""
    s = _seed(today_stem, today_branch, user_stem, user_branch)
    return {
        "color": _COLORS[s % len(_COLORS)],
        "number": (s // 7) % 99 + 1,          # 1~99
        "direction": _DIRECTIONS[(s // 13) % len(_DIRECTIONS)],
        "food": {"name": _FOODS[(s // 17) % len(_FOODS)]},
    }
