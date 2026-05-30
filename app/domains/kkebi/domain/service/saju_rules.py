"""사주 룰: 십성 + 지지관계 매핑 (순수 Python — 외부 import 금지).

scripts/kkebi_pilot/saju_rules.py 의 검증된 로직을 app 본체로 이식.
FortuneTeller 응답이 한글 천간/지지("갑","자")를 주므로 한글→한자 정규화 헬퍼 포함.

- 십성: 사용자 일간 × 오늘 일진 천간 → 10종 중 1
- 지지관계: 사용자 일지 × 오늘 일진 지지 → 합/충/형/파/해/동주/보통 중 1
"""
from __future__ import annotations

# 한글 → 한자 정규화 (FortuneTeller가 한글 표기로 줄 때)
STEM_HANGUL_TO_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}
BRANCH_HANGUL_TO_HANJA: dict[str, str] = {
    "자": "子", "축": "丑", "인": "寅", "묘": "卯", "진": "辰", "사": "巳",
    "오": "午", "미": "未", "신": "申", "유": "酉", "술": "戌", "해": "亥",
}


def normalize_stem(stem: str) -> str:
    """천간을 한자로 정규화 (이미 한자면 그대로)."""
    return STEM_HANGUL_TO_HANJA.get(stem, stem)


def normalize_branch(branch: str) -> str:
    """지지를 한자로 정규화 (이미 한자면 그대로)."""
    return BRANCH_HANGUL_TO_HANJA.get(branch, branch)


# 천간 음양 (양: 갑병무경임 / 음: 을정기신계)
STEM_YIN_YANG: dict[str, str] = {
    "甲": "양", "乙": "음", "丙": "양", "丁": "음", "戊": "양",
    "己": "음", "庚": "양", "辛": "음", "壬": "양", "癸": "음",
}

# 천간 오행
STEM_WUXING: dict[str, str] = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

# 지지 오행
BRANCH_WUXING: dict[str, str] = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

WUXING_KOREAN: dict[str, str] = {
    "木": "목", "火": "화", "土": "토", "金": "금", "水": "수",
}


def derive_sipseong(user_stem: str, today_stem: str) -> str:
    """사용자 일간 기준 오늘 천간의 십성. 입력은 한글/한자 모두 허용."""
    u = normalize_stem(user_stem)
    t = normalize_stem(today_stem)
    user_wx = STEM_WUXING[u]
    today_wx = STEM_WUXING[t]
    same_yy = STEM_YIN_YANG[u] == STEM_YIN_YANG[t]

    if user_wx == today_wx:
        return "비견" if same_yy else "겁재"
    生_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    克_map = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
    if 生_map[user_wx] == today_wx:
        return "식신" if same_yy else "상관"
    if 克_map[user_wx] == today_wx:
        return "편재" if same_yy else "정재"
    if 生_map[today_wx] == user_wx:
        return "편인" if same_yy else "정인"
    if 克_map[today_wx] == user_wx:
        return "편관" if same_yy else "정관"
    return "보통"


BRANCH_HEAP: dict[str, str] = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}
BRANCH_CHONG: dict[str, str] = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}
BRANCH_HYEONG: dict[str, list[str]] = {
    "子": ["卯"], "卯": ["子"],
    "寅": ["巳"], "巳": ["申"], "申": ["寅"],
    "丑": ["戌"], "戌": ["未"], "未": ["丑"],
    "辰": ["辰"], "午": ["午"], "酉": ["酉"], "亥": ["亥"],
}
BRANCH_PA: dict[str, str] = {
    "子": "酉", "酉": "子", "午": "卯", "卯": "午",
    "申": "巳", "巳": "申", "寅": "亥", "亥": "寅",
    "辰": "丑", "丑": "辰", "戌": "未", "未": "戌",
}
BRANCH_HAE: dict[str, str] = {
    "子": "未", "未": "子", "丑": "午", "午": "丑",
    "寅": "巳", "巳": "寅", "卯": "辰", "辰": "卯",
    "申": "亥", "亥": "申", "酉": "戌", "戌": "酉",
}


def derive_branch_relation(user_branch: str, today_branch: str) -> str:
    """사용자 일지 기준 오늘 지지의 관계. 입력은 한글/한자 모두 허용."""
    u = normalize_branch(user_branch)
    t = normalize_branch(today_branch)
    if u == t:
        return "동주"
    if BRANCH_HEAP.get(u) == t:
        return "합"
    if BRANCH_CHONG.get(u) == t:
        return "충"
    if t in BRANCH_HYEONG.get(u, []):
        return "형"
    if BRANCH_PA.get(u) == t:
        return "파"
    if BRANCH_HAE.get(u) == t:
        return "해"
    return "보통"
