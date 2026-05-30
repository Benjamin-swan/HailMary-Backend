"""사주 룰: 십성 + 지지관계 매핑.

- 십성: 사용자 일간 × 오늘 일진 천간 → 10종 중 1
- 지지관계: 사용자 일지 × 오늘 일진 지지 → 합/충/형/파/해/같음/보통 중 1

룰은 정통 사주 명리 기준 (학습용 참고서 수준 단순화).
"""

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

WUXING_KOREAN: dict[str, str] = {
    "木": "목", "火": "화", "土": "토", "金": "금", "水": "수",
}

# 십성 산출 (사용자 일간 기준 오늘 천간이 무엇인지)
# 오행 관계: 同(비), 生(식), 克(재), 被生(인), 被克(관)
# 같은 음양: 비견/식신/편재/편인/편관
# 다른 음양: 겁재/상관/정재/정인/정관
def derive_sipseong(user_stem: str, today_stem: str) -> str:
    user_wx = STEM_WUXING[user_stem]
    today_wx = STEM_WUXING[today_stem]
    user_yy = STEM_YIN_YANG[user_stem]
    today_yy = STEM_YIN_YANG[today_stem]
    same_yy = user_yy == today_yy

    if user_wx == today_wx:
        return "비견" if same_yy else "겁재"
    # 用 -> Today (사용자가 生하는 오행)
    生_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    克_map = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
    if 生_map[user_wx] == today_wx:
        return "식신" if same_yy else "상관"
    if 克_map[user_wx] == today_wx:
        return "편재" if same_yy else "정재"
    if 生_map[today_wx] == user_wx:  # Today가 사용자를 生
        return "편인" if same_yy else "정인"
    if 克_map[today_wx] == user_wx:  # Today가 사용자를 克
        return "편관" if same_yy else "정관"
    return "보통"


# 지지관계
# 같음(동주), 6합, 충, 형, 파, 해, 삼합/방합 일부, 보통
BRANCH_HEAP: dict[str, str] = {  # 6합
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}
BRANCH_CHONG: dict[str, str] = {  # 충
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}
BRANCH_HYEONG: dict[str, list[str]] = {  # 형 (대표만)
    "子": ["卯"], "卯": ["子"],
    "寅": ["巳"], "巳": ["申"], "申": ["寅"],
    "丑": ["戌"], "戌": ["未"], "未": ["丑"],
    "辰": ["辰"], "午": ["午"], "酉": ["酉"], "亥": ["亥"],
}
BRANCH_PA: dict[str, str] = {  # 파
    "子": "酉", "酉": "子", "午": "卯", "卯": "午",
    "申": "巳", "巳": "申", "寅": "亥", "亥": "寅",
    "辰": "丑", "丑": "辰", "戌": "未", "未": "戌",
}
BRANCH_HAE: dict[str, str] = {  # 해
    "子": "未", "未": "子", "丑": "午", "午": "丑",
    "寅": "巳", "巳": "寅", "卯": "辰", "辰": "卯",
    "申": "亥", "亥": "申", "酉": "戌", "戌": "酉",
}


def derive_branch_relation(user_branch: str, today_branch: str) -> str:
    if user_branch == today_branch:
        return "동주"  # 본인과 같은 지지
    if BRANCH_HEAP.get(user_branch) == today_branch:
        return "합"
    if BRANCH_CHONG.get(user_branch) == today_branch:
        return "충"
    if today_branch in BRANCH_HYEONG.get(user_branch, []):
        return "형"
    if BRANCH_PA.get(user_branch) == today_branch:
        return "파"
    if BRANCH_HAE.get(user_branch) == today_branch:
        return "해"
    return "보통"
