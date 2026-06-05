from typing import Any

from app.domains.user.domain.entity.user import User

# 사주 8글자 한자 매핑 (saju_view_mapper와 일치, Domain은 외부 import 금지라 자체 보유).
_STEM_HANGUL_TO_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}

_BRANCH_HANGUL_TO_HANJA: dict[str, str] = {
    "자": "子", "축": "丑", "인": "寅", "묘": "卯", "진": "辰", "사": "巳",
    "오": "午", "미": "未", "신": "申", "유": "酉", "술": "戌", "해": "亥",
}

# 천간(stem) → 일간 한글 풀네임 (예: "갑" → "갑목").
_STEM_TO_ILGAN: dict[str, str] = {
    "갑": "갑목", "을": "을목",
    "병": "병화", "정": "정화",
    "무": "무토", "기": "기토",
    "경": "경금", "신": "신금",
    "임": "임수", "계": "계수",
}

_OHANG_KEYS = ("목", "화", "토", "금", "수")


class SajuDataExtractor:
    """User 엔티티를 FortuneTeller 요청 형식으로 변환 + 분석 raw로부터 P-0 변수 추출."""

    def extract(self, user: User) -> dict:  # type: ignore[type-arg]
        birth_time = user.birth_info.birth_time_str()
        return {
            "birth": user.birth_info.birth_date.strftime("%Y-%m-%d"),
            "time": birth_time if birth_time is not None else "unknown",
            "calendar": user.birth_info.calendar_type.value,
            "gender": user.gender.value,
        }

    def extract_paid_variables(self, saju_raw: dict[str, Any]) -> dict[str, Any]:
        """FortuneTeller raw 응답 → P-0 프롬프트 변수 16개.

        반환 키:
            SI_G/SI_J: 시주 천간/지지 한자
            IL_G/IL_J: 일주 천간/지지 한자
            WL_G/WL_J: 월주 천간/지지 한자
            YR_G/YR_J: 년주 천간/지지 한자
            OHANG_MOK/HWA/TO/GEUM/SU: 오행 비율 정수(0~100, 합 100)
            OHANG_EXCESS: 비율 max인 오행 한글 1글자 (서사 포커스용 — 지배적 1개)
            OHANG_LACK: 비율 min인 오행 한글 1글자 (서사 포커스용 — 지배적 1개)
            OHANG_JUDGMENTS: 오행별 강약 판정 dict (한글키 → 결핍/적정/발달/과다)
                             — P-0 "0-2 오행의 흐름" 막대 표시용. 무료 결과와 동일 임계값.
            ILGAN: 일간 한글 풀네임 (10종 중 하나, 예: "임수")
            ILJU: 일주 한글 (천간+지지, 예: "임술")

        누락된 raw 필드는 빈 문자열로 채우거나 기본값으로 둔다.
        개인정보(생년월일·이름·성별)는 결과에 포함하지 않는다.
        """

        year = _safe_dict(saju_raw.get("year"))
        month = _safe_dict(saju_raw.get("month"))
        day = _safe_dict(saju_raw.get("day"))
        hour = _safe_dict(saju_raw.get("hour"))

        wuxing_count = _safe_dict(saju_raw.get("wuxingCount"))
        ratios = _ohang_ratios_percent(wuxing_count)
        excess, lack = _ohang_excess_lack(ratios)
        judgments = classify_ohang_strength(wuxing_count)

        day_stem = str(day.get("stem", ""))
        day_branch = str(day.get("branch", ""))
        ilgan = _STEM_TO_ILGAN.get(day_stem, "")
        ilju = day_stem + day_branch if day_stem and day_branch else ""

        return {
            "SI_G": _stem_hanja(hour),
            "SI_J": _branch_hanja(hour),
            "IL_G": _stem_hanja(day),
            "IL_J": _branch_hanja(day),
            "WL_G": _stem_hanja(month),
            "WL_J": _branch_hanja(month),
            "YR_G": _stem_hanja(year),
            "YR_J": _branch_hanja(year),
            "OHANG_MOK": ratios["목"],
            "OHANG_HWA": ratios["화"],
            "OHANG_TO": ratios["토"],
            "OHANG_GEUM": ratios["금"],
            "OHANG_SU": ratios["수"],
            "OHANG_EXCESS": excess,
            "OHANG_LACK": lack,
            "OHANG_JUDGMENTS": judgments,
            "ILGAN": ilgan,
            "ILJU": ilju,
        }


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _stem_hanja(pillar: dict[str, Any]) -> str:
    stem = str(pillar.get("stem", ""))
    return _STEM_HANGUL_TO_HANJA.get(stem, "")


def _branch_hanja(pillar: dict[str, Any]) -> str:
    branch = str(pillar.get("branch", ""))
    return _BRANCH_HANGUL_TO_HANJA.get(branch, "")


def _ohang_ratios_percent(wuxing_count: dict[str, Any]) -> dict[str, int]:
    """wuxingCount({"목":1, "화":2, ...}) → 정수 % (합 100)."""
    counts = {key: _to_int(wuxing_count.get(key, 0)) for key in _OHANG_KEYS}
    total = sum(counts.values())
    if total == 0:
        return dict.fromkeys(_OHANG_KEYS, 0)
    # round() 후 합이 100과 어긋날 수 있어 가장 큰 항목에 잔차를 흡수.
    raw = {key: counts[key] / total * 100 for key in _OHANG_KEYS}
    rounded = {key: int(round(raw[key])) for key in _OHANG_KEYS}
    diff = 100 - sum(rounded.values())
    if diff != 0:
        target = max(_OHANG_KEYS, key=lambda k: raw[k])
        rounded[target] += diff
    return rounded


def _ohang_excess_lack(ratios: dict[str, int]) -> tuple[str, str]:
    """비율 max/min 오행 한글 1글자. 모두 0이면 빈 문자열.

    NOTE: 단일 지배 오행(서사 포커스)용. P-0 ai_intro / P-3(과다) / P-9(부족)
    템플릿이 '1개'를 전제로 쓰므로 의도적으로 단일값을 유지한다.
    오행 강약 '표시'(막대 라벨)는 classify_ohang_strength()를 써야 한다.
    """
    if all(v == 0 for v in ratios.values()):
        return "", ""
    excess = max(_OHANG_KEYS, key=lambda k: ratios[k])
    lack = min(_OHANG_KEYS, key=lambda k: ratios[k])
    return excess, lack


def classify_ohang_strength(wuxing_count: dict[str, Any]) -> dict[str, str]:
    """오행별 강약 판정(한글키 → 결핍/적정/발달/과다).

    임계값: <5 결핍 · <20 적정 · <32 발달 · ≥32 과다.
    비율 = count/total*100 (소수 1자리 반올림 후 판정).

    무료 결과 페이지와 동일 기준이어야 사용자 교차검증에서 어긋나지 않는다.
    **SSOT 동기화 대상**: app/domains/user/application/saju_view_mapper.py
    의 `_build_wuxing()` judge()와 임계값·라운딩이 반드시 일치해야 한다
    (둘 다 수정 시 tests/domains/user/test_ohang_judgments.py 동일성 테스트로 보증).

    카운트 합이 0이면 모든 오행을 "결핍"으로 둔다.
    """
    counts = {key: _to_int(wuxing_count.get(key, 0)) for key in _OHANG_KEYS}
    total = sum(counts.values()) or 1

    def judge(ratio: float) -> str:
        if ratio < 5:
            return "결핍"
        if ratio < 20:
            return "적정"
        if ratio < 32:
            return "발달"
        return "과다"

    return {key: judge(round(counts[key] / total * 100, 1)) for key in _OHANG_KEYS}


def _to_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0
