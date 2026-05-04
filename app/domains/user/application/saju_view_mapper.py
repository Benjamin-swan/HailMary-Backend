"""FortuneTeller raw 응답 → 프론트엔드 expected shape 변환.

FortuneTeller가 반환하는 한글 기반 raw dict를 프론트의 Pillar/Wuxing/YongSin/DayMaster
shape으로 변환한다. 영업비밀(점수, 분석 텍스트, 격국 세부, 지장간 등)은 출력에서 제외.

Frontend 미제공 필드(daeUn, twelvePhase 상세, sinSals 기둥별 분배, highlight)는
출력에 포함하지 않아 프론트 hook의 mock fallback이 살아있도록 한다.
"""

from __future__ import annotations

from typing import Any, cast

# ── 매핑 테이블 ──────────────────────────────────────────────────

STEM_HANGUL_TO_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}

BRANCH_HANGUL_TO_HANJA: dict[str, str] = {
    "자": "子", "축": "丑", "인": "寅", "묘": "卯", "진": "辰", "사": "巳",
    "오": "午", "미": "未", "신": "申", "유": "酉", "술": "戌", "해": "亥",
}

ELEMENT_TO_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}

# 오행별 색상 (mock 코드에서 차용)
ELEMENT_HUE: dict[str, str] = {
    "목": "#9CC8B0",
    "화": "#E6A88E",
    "토": "#E6C58E",
    "금": "#C5CAD4",
    "수": "#6B8BB5",
}

TEN_GOD_TO_HANJA: dict[str, str] = {
    "비견": "比肩", "겁재": "劫財",
    "식신": "食神", "상관": "傷官",
    "편재": "偏財", "정재": "正財",
    "편관": "偏官", "정관": "正官",
    "편인": "偏印", "정인": "正印",
}

# 지지 음양 (자/인/진/오/신/술 = 양, 축/묘/사/미/유/해 = 음)
BRANCH_YIN_YANG: dict[str, str] = {
    "자": "양", "축": "음", "인": "양", "묘": "음",
    "진": "양", "사": "음", "오": "양", "미": "음",
    "신": "양", "유": "음", "술": "양", "해": "음",
}

# 오행 상극: A를 극하는 것 — 용신(A)의 기신은 A를 극하는 오행
# 금극목, 수극화, 목극토, 화극금, 토극수
ELEMENT_RESTRAINER: dict[str, str] = {
    "목": "금", "화": "수", "토": "목", "금": "화", "수": "토",
}

# 강도 레벨 7단계 (score 기반 버킷)
_STRENGTH_BUCKETS: list[tuple[int, str, int]] = [
    (20, "극약", 1),
    (35, "태약", 2),
    (45, "신약", 3),
    (55, "중화", 4),
    (65, "신강", 5),
    (80, "태강", 6),
    (101, "극왕", 7),
]

# raw level 문자열 → 기본 score (score 누락 시)
_LEVEL_DEFAULT_SCORE: dict[str, int] = {
    "very_weak": 10,
    "weak": 25,
    "slightly_weak": 38,
    "medium": 50,
    "slightly_strong": 60,
    "strong": 73,
    "very_strong": 90,
}


# ── 변환 함수 ───────────────────────────────────────────────────


def _build_pillar(
    label: str,
    pillar_raw: dict[str, Any],
    ten_god_heaven: str | None,
) -> dict[str, Any]:
    stem = str(pillar_raw.get("stem", ""))
    branch = str(pillar_raw.get("branch", ""))
    stem_element = str(pillar_raw.get("stemElement", ""))
    branch_element = str(pillar_raw.get("branchElement", ""))
    stem_yin_yang = str(pillar_raw.get("yinYang", "양"))

    return {
        "label": label,
        "heaven": STEM_HANGUL_TO_HANJA.get(stem, stem),
        "earth": BRANCH_HANGUL_TO_HANJA.get(branch, branch),
        "heavenHangul": stem,
        "earthHangul": branch,
        "element": f"{stem_element} / {branch_element}".strip(" /"),
        "hue": ELEMENT_HUE.get(stem_element, "#888888"),
        "yinYang": {
            "heaven": stem_yin_yang,
            "earth": BRANCH_YIN_YANG.get(branch, "양"),
        },
        "tenGod": {
            "heaven": ten_god_heaven or "",
            "earth": "",  # raw에 직접 없음 — 추후 지장간 기반 산출 가능
            "heavenHanja": TEN_GOD_TO_HANJA.get(ten_god_heaven or "", ""),
            "earthHanja": "",
        },
        "twelvePhase": {"name": "", "hanja": ""},
        "sinSals": [],
        "unknown": False,
    }


def _build_wuxing(wuxing_count: dict[str, Any]) -> dict[str, Any]:
    elements = ["목", "화", "토", "금", "수"]
    counts = {e: int(wuxing_count.get(e, 0) or 0) for e in elements}
    total = sum(counts.values()) or 1

    ratios = {e: round(counts[e] / total * 100, 1) for e in elements}

    def judge(ratio: float) -> str:
        if ratio < 5:
            return "결핍"
        if ratio < 20:
            return "적정"
        if ratio < 32:
            return "발달"
        return "과다"

    judgments = {e: judge(ratios[e]) for e in elements}
    return {"counts": counts, "ratios": ratios, "judgments": judgments}


def _build_yongsin(yong_sin_raw: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(yong_sin_raw, dict):
        return None
    primary = yong_sin_raw.get("primaryYongSin")
    secondary = yong_sin_raw.get("secondaryYongSin")
    if not isinstance(primary, str) or primary not in ELEMENT_TO_HANJA:
        return None

    primary_slot = {
        "element": primary,
        "hanja": ELEMENT_TO_HANJA[primary],
        "role": "용신",
    }
    secondary_slot = None
    if isinstance(secondary, str) and secondary in ELEMENT_TO_HANJA:
        secondary_slot = {
            "element": secondary,
            "hanja": ELEMENT_TO_HANJA[secondary],
            "role": "희신",
        }

    opposing_element = ELEMENT_RESTRAINER.get(primary, primary)
    opposing_slot = {
        "element": opposing_element,
        "hanja": ELEMENT_TO_HANJA[opposing_element],
        "role": "기신",
    }
    return {"primary": primary_slot, "secondary": secondary_slot, "opposing": opposing_slot}


def _build_day_master(day_pillar: dict[str, Any], strength_raw: dict[str, Any]) -> dict[str, Any]:
    stem = str(day_pillar.get("stem", ""))
    score_val = strength_raw.get("score") if isinstance(strength_raw, dict) else None
    if not isinstance(score_val, (int, float)):
        level = strength_raw.get("level") if isinstance(strength_raw, dict) else None
        score_val = _LEVEL_DEFAULT_SCORE.get(str(level), 50)
    score = int(score_val)

    for threshold, label, position in _STRENGTH_BUCKETS:
        if score < threshold:
            strength_label = label
            strength_position = position
            break
    else:
        strength_label = "극왕"
        strength_position = 7

    return {
        "stem": stem,
        "stemHanja": STEM_HANGUL_TO_HANJA.get(stem, stem),
        "strengthLevel": strength_label,
        "strengthScale": 7,
        "strengthPosition": strength_position,
    }


def to_view(saju_data: dict[str, Any]) -> dict[str, Any]:
    """FortuneTeller raw → 프론트 expected shape.

    누락 raw 필드는 빈 값으로 채우거나 키를 포함하지 않아 프론트 mock fallback 작동.
    영업비밀 키(gyeokGuk, jiJangGan, branchRelations, wolRyeong, dayMasterStrength.score
    /analysis, yongSin.reasoning)는 출력에서 제외.
    """
    ten_gods = saju_data.get("tenGods")
    if not isinstance(ten_gods, list):
        ten_gods = []
    ten_gods_padded: list[str | None] = [
        cast(str, v) if isinstance(v, str) else None
        for v in (ten_gods + [None] * 4)[:4]
    ]

    pillars = [
        _build_pillar("년주", _safe_dict(saju_data.get("year")), ten_gods_padded[0]),
        _build_pillar("월주", _safe_dict(saju_data.get("month")), ten_gods_padded[1]),
        _build_pillar("일주", _safe_dict(saju_data.get("day")), ten_gods_padded[2]),
        _build_pillar("시주", _safe_dict(saju_data.get("hour")), ten_gods_padded[3]),
    ]

    wuxing = _build_wuxing(_safe_dict(saju_data.get("wuxingCount")))
    yong_sin = _build_yongsin(_safe_dict(saju_data.get("yongSin")))
    day_master = _build_day_master(
        _safe_dict(saju_data.get("day")),
        _safe_dict(saju_data.get("dayMasterStrength")),
    )

    view: dict[str, Any] = {
        "pillars": pillars,
        "wuxing": wuxing,
        "dayMaster": day_master,
    }
    if yong_sin is not None:
        view["yongSin"] = yong_sin
    return view


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
