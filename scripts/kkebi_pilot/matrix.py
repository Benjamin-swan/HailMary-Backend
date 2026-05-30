"""사용자 × 오늘 일진 → 슬롯별 셀 키 산출.

슬롯 키 정의:
- A 헤드라인: (sipseong, branch_rel)
- B 시간대 분위기: (time_slot, mood3)  // mood3은 점수 산출 후 분기
- C 시간대 액션: (time_slot, mood3)
- D 영역 헤드: (area, mood3)
- E 卜 관찰: (area, sipseong)
- F 警 경계: (area, sipseong)
- G 助 조언: (area, sipseong)
"""
from .saju_rules import derive_sipseong, derive_branch_relation
from .users import PilotUser, TODAY_STEM, TODAY_BRANCH

AREAS = ["love", "work", "money", "health", "study"]
AREA_KOREAN = {"love": "연애", "work": "일·업무", "money": "재물·돈", "health": "건강·컨디션", "study": "학습·자기개발"}
TIME_SLOTS = ["morning", "afternoon", "night"]
TIME_KOREAN = {"morning": "오전", "afternoon": "오후", "night": "저녁/밤"}


def derive_user_keys(user: PilotUser) -> dict:
    sipseong = derive_sipseong(user.day_stem, TODAY_STEM)
    branch_rel = derive_branch_relation(user.day_branch, TODAY_BRANCH)
    return {
        "sipseong": sipseong,
        "branch_rel": branch_rel,
    }


# 점수 하한 70 — 사용자가 필요 이상으로 기분 나빠지지 않도록 (floor 70, ceil 95)
SCORE_FLOOR = 70
SCORE_CEIL = 95


def mood3_from_score(score: int) -> str:
    # floor가 70이라 '낮음(우울)' 톤은 의도적으로 배제 — 최저여도 톤은 중립.
    # 70~79=보통, 80+=좋음. (사용자가 필요 이상으로 기분 나빠지지 않게)
    if score >= 80: return "good"
    return "mid"


# 룰 기반 점수 산출 (단순 데모용)
def score_total(sipseong: str, branch_rel: str) -> int:
    base = {"비견": 60, "겁재": 50, "식신": 75, "상관": 65, "편재": 60, "정재": 70,
            "편관": 50, "정관": 72, "편인": 58, "정인": 70, "보통": 60}.get(sipseong, 60)
    adj = {"합": 8, "동주": 4, "보통": 0, "파": -6, "해": -6, "형": -8, "충": -12}.get(branch_rel, 0)
    return max(SCORE_FLOOR, min(SCORE_CEIL, base + adj))


def score_area(sipseong: str, area: str) -> int:
    # 영역×십성별 가중치 (단순 데모용 — 실제 룰북은 별도)
    base = {"비견": 60, "겁재": 50, "식신": 75, "상관": 65, "편재": 60, "정재": 70,
            "편관": 50, "정관": 72, "편인": 58, "정인": 70, "보통": 60}.get(sipseong, 60)
    bias = {
        "love":    {"정관": 8, "정재": 6, "상관": -6, "편관": -4},
        "work":    {"정관": 8, "식신": 6, "겁재": -6, "편관": 4},
        "money":   {"정재": 10, "편재": 8, "겁재": -10, "비견": -4},
        "health":  {"식신": 8, "정인": 6, "편관": -8, "상관": -4},
        "study":   {"정인": 10, "편인": 6, "상관": 4, "겁재": -4},
    }.get(area, {})
    return max(SCORE_FLOOR, min(SCORE_CEIL, base + bias.get(sipseong, 0)))


def score_time(user_sipseong: str, time_slot: str) -> int:
    # 시간대별 가중치 (단순 데모)
    base = {"비견": 60, "겁재": 50, "식신": 75, "상관": 65, "편재": 60, "정재": 70,
            "편관": 50, "정관": 72, "편인": 58, "정인": 70, "보통": 60}.get(user_sipseong, 60)
    bias = {"morning": 5, "afternoon": -3, "night": 0}.get(time_slot, 0)
    return max(SCORE_FLOOR, min(SCORE_CEIL, base + bias))


def slot_keys_for_user(user: PilotUser) -> dict:
    """이 사용자의 결과지에 필요한 모든 슬롯 셀 키."""
    derived = derive_user_keys(user)
    sipseong = derived["sipseong"]
    branch_rel = derived["branch_rel"]
    total = score_total(sipseong, branch_rel)
    total_mood = mood3_from_score(total)

    cells = {
        "A_headline": (sipseong, branch_rel),
        "B_time": [],  # (time_slot, mood3)
        "C_time_tip": [],
        "D_area_head": [],  # (area, mood3)
        "E_bok": [],   # (area, sipseong)
        "F_gyeong": [],
        "G_jo": [],
    }
    for ts in TIME_SLOTS:
        m = mood3_from_score(score_time(sipseong, ts))
        cells["B_time"].append((ts, m))
        cells["C_time_tip"].append((ts, m))
    for area in AREAS:
        m = mood3_from_score(score_area(sipseong, area))
        cells["D_area_head"].append((area, m))
        cells["E_bok"].append((area, sipseong))
        cells["F_gyeong"].append((area, sipseong))
        cells["G_jo"].append((area, sipseong))

    return {
        "sipseong": sipseong,
        "branch_rel": branch_rel,
        "total_score": total,
        "total_mood": total_mood,
        "cells": cells,
    }
