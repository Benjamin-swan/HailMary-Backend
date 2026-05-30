"""점수/무드 룰 (순수 Python).

scripts/kkebi_pilot/matrix.py 의 점수 로직 이식. 점수 하한 70 정책 유지
(사용자가 필요 이상으로 기분 나빠지지 않게).
"""
from __future__ import annotations

SCORE_FLOOR = 70
SCORE_CEIL = 99

AREAS = ["love", "work", "money", "health", "study"]
TIME_SLOTS = ["morning", "afternoon", "night"]

# 십성별 기본 점수 (80~94 밴드 — 고객경험상 점수가 70에 몰리지 않고
# 70~99에 20/50/30 분포로 퍼지도록 재설계. 십성 길흉 순서는 유지).
_SIPSEONG_BASE: dict[str, int] = {
    "식신": 94, "정관": 93, "정재": 92, "정인": 90, "상관": 88,
    "편재": 86, "비견": 85, "편인": 84, "편관": 82, "겁재": 80, "보통": 85,
}
# 지지관계 보정 (충/형이 70대로 내려가 변별이 생기도록 음수 폭 유지)
_BRANCH_ADJ: dict[str, int] = {
    "합": 5, "동주": 3, "보통": 0, "파": -4, "해": -5, "형": -7, "충": -10,
}
# 영역×십성 가중치 (dense — 십성마다 5영역[love,work,money,health,study] 전부 보정).
# 희소 테이블은 6/10 십성이 보정 0이라 영역 점수가 평평해짐 → 50칸 모두 채워
# 십성마다 영역값이 서로 다르게(최소 4종) 나오게 한다. 명리 성격 반영 + ±값 분산.
_AREA_BIAS: dict[str, list[int]] = {
    #          love  work  money health study
    "식신":   [  2,    5,   -3,    8,   -1],   # 표현·여유: 건강·일↑, 돈↓
    "정관":   [  7,    9,   -2,    1,    4],   # 명예·질서: 일·연애↑
    "정재":   [  5,    2,    9,    3,   -2],   # 성실·재물: 돈↑
    "정인":   [  1,   -1,   -3,    6,    9],   # 학습·수용: 학습·건강↑
    "상관":   [ -5,    3,    1,   -2,    7],   # 재능발산: 학습↑, 연애↓
    "편재":   [  4,    1,    8,   -1,   -3],   # 활동·기회: 돈↑
    "비견":   [  2,    4,   -4,    1,   -1],   # 자립·경쟁: 일↑, 돈↓
    "편인":   [ -2,    1,   -3,    2,    6],   # 직관·궁리: 학습↑
    "편관":   [  3,    6,   -1,   -4,    2],   # 도전·압박: 일↑, 건강↓
    "겁재":   [ -1,    2,   -6,    3,   -2],   # 경쟁·돌발: 돈↓
}
# 시간대 가중치
_TIME_BIAS: dict[str, int] = {"morning": 5, "afternoon": -3, "night": 0}

# 영역/시간대 점수 전용 base 차감.
# total은 관계보정(충 -10 등)으로 끌어내려지지만 area/time은 양수 bias만 있어
# 그대로면 90대에 몰린다. 종합점수와 균형 맞추고 70~99에 20/50/30 분포되도록 차감.
_SUBSCORE_OFFSET = 6


def _clamp(v: int) -> int:
    return max(SCORE_FLOOR, min(SCORE_CEIL, v))


def score_total(sipseong: str, branch_rel: str) -> int:
    return _clamp(_SIPSEONG_BASE.get(sipseong, 60) + _BRANCH_ADJ.get(branch_rel, 0))


def score_area(sipseong: str, area: str) -> int:
    base = _SIPSEONG_BASE.get(sipseong, 60) - _SUBSCORE_OFFSET
    row = _AREA_BIAS.get(sipseong)
    bias = row[AREAS.index(area)] if row and area in AREAS else 0
    return _clamp(base + bias)


def score_time(sipseong: str, time_slot: str) -> int:
    base = _SIPSEONG_BASE.get(sipseong, 60) - _SUBSCORE_OFFSET
    return _clamp(base + _TIME_BIAS.get(time_slot, 0))
