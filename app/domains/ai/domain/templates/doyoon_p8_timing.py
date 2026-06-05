"""도윤 P-8 五 인연이 오는 시간 — 룰 합성 + facts.

원본 도윤_final.html data-page-idx=8 구조 정합.
연우 P-8 헬퍼 재사용 (_pct_to_hearts_p8 / _pick_top_two_peaks /
_classify_state / _format_month_label / _peak_label_for_ai).
도윤 톤 텍스트만 신규.
"""

from __future__ import annotations

from typing import Any

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.templates.yeonwoo_p8_timing import (
    VALID_ILGAN,
    _classify_state,
    _format_month_label,
    _pct_to_hearts_p8,
    _peak_label_for_ai,
    _pick_top_two_peaks,
)

# ── 도윤 톤 텍스트 ────────────────────────────────────────────


PARA_1_FIXED_DOYOON = (
    "앞으로 1년, 새 인연이 들어오기 좋은 시기를 달별로 정리해드릴게요. 이번 달부터 1년이에요."
)

PARA_2_TEMPLATE_DOYOON = (
    "1년 중에서 인연의 흐름이 특히 도드라지는 시기가 두 번 있어요. {peak_1}과 {peak_2}. "
    "이 두 달은 새 인연을 만날 가능성이 한 해 중 가장 크게 올라가는 때예요. "
    "그 사이 시기는 마음을 차분히 정리하고 자신을 가다듬으며 다음을 준비하기 좋은 때고요."
)

BUBBLE_DOYOON = "이 시기에 새 인연을 만날 가능성이 가장 크게 올라가요."

# 일간별 흐름 결 (3단락 마지막 단락)
ILGAN_FLOW_BY_ILGAN_DOYOON: dict[str, str] = {
    "갑목": (
        "{ilgan_with_hanja} 일간은 곧장 다가가는 방식이 가장 잘 통해요. "
        "흐름이 도드라지는 시기엔 마음을 한 방향으로 모아 다가가시는 게 좋아요."
    ),
    "을목": (
        "{ilgan_with_hanja} 일간은 상황에 맞춰 유연하게 움직일 때 인연이 잘 풀려요. "
        "좋은 시기엔 흐름에 맞게 부드럽게 가되, 한 번 마음이 향한 신호는 끝까지 이어가시는 게 좋아요."
    ),
    "병화": (
        "{ilgan_with_hanja} 일간은 마음을 빠르게 표현할 때 가장 잘 맞아요. "
        "기회가 커지는 시기엔 마음이 식기 전에 바로 신호를 전하시는 게 좋아요."
    ),
    "정화": (
        "{ilgan_with_hanja} 일간은 한 사람에게 집중할 때 인연이 가장 깊어져요. "
        "흐름이 좋은 시기엔 마음이 가는 한 사람에게 조용히, 깊게 다가가시는 게 좋아요."
    ),
    "무토": (
        "{ilgan_with_hanja} 일간은 흐름을 억지로 거스를수록 오히려 힘들어지기 쉬워요. "
        "좋은 시기엔 한 걸음씩 천천히 다가가시는 게 가장 잘 맞아요."
    ),
    "기토": (
        "{ilgan_with_hanja} 일간은 따뜻한 마음을 건넬 때 인연이 잘 열려요. "
        "흐름이 도드라지는 시기엔 작은 배려 한 번이 마음을 움직이는 계기가 돼요."
    ),
    "경금": (
        "{ilgan_with_hanja} 일간은 마음을 분명하게 드러낼 때 인연이 잘 맞아떨어져요. "
        "기회가 커지는 시기엔 망설이지 말고 솔직하게 마음을 전하시는 게 좋아요."
    ),
    "신금": (
        "{ilgan_with_hanja} 일간은 세심한 신호를 건넬 때 마음이 닿아요. "
        "흐름이 좋은 시기엔 섬세한 표현 한 번이 결정적인 순간이 돼요."
    ),
    "임수": (
        "{ilgan_with_hanja} 일간은 흐름을 억지로 거스를수록 오히려 지치기 쉬워요. "
        "좋은 시기엔 마음을 적극적으로 내고, 잔잔한 시기엔 자신을 차분히 가다듬는 게 가장 잘 맞아요."
    ),
    "계수": (
        "{ilgan_with_hanja} 일간은 은근한 끌림을 잘 살릴 때 인연이 풀려요. "
        "흐름이 도드라지는 시기엔 작은 끌림을 분명한 신호로 바꿔 보이시는 게 좋아요."
    ),
}

# 월별 코멘트 풀 (state 기반 매핑 — 연우와 동일 키 사용, 도윤 톤으로 재작성)
STATE_DESC_BY_STATE_DOYOON: dict[str, str] = {
    "시작": "이번 달부터 흐름이 슬슬 움직이기 시작해요. 큰 변화는 없지만 분위기가 조금씩 달라져요.",
    "상승": "새 인연을 만날 가능성이 차오르는 때예요. 자주 마주치는 사람이 인연으로 이어지는 경우가 많아요.",
    "진입": "인연의 흐름이 빠르게 차오르는 시기예요. 다가오는 신호를 놓치지 않도록 마음을 열어두세요.",
    "피크": "한 해 중 흐름이 가장 도드라지는 때예요. 이 시기엔 마음을 솔직하게 표현할수록 잘 통해요.",
    "심화": "관계가 한 걸음 더 깊어지는 때예요. 상대의 속도를 존중하며 가는 게 좋아요.",
    "안정": "관계가 차분하게 자리를 잡는 때예요. 지금 흐름을 그대로 이어가는 게 가장 좋아요.",
    "정체": "잠시 흐름이 잔잔해지는 때예요. 조급하게 밀어붙이면 오히려 어긋나기 쉬워요.",
    "충전": "새로운 환경에 발을 들이기 좋은 때예요. 동선을 조금 바꾸면 새 인연의 계기가 다시 생겨요.",
    "2차 피크": "해가 바뀌며 흐름이 다시 한 번 도드라지는 때예요. 마음을 분명하게 표현하는 게 중요해요.",
    "1년차 마무리": "1년의 흐름이 마무리되는 때예요. 솔직한 표현이 다음 흐름을 여는 열쇠가 돼요.",
}


def _ilgan_with_hanja_doyoon(ilgan: str) -> str:
    return f"{ilgan}({ILGAN_HANJA[ilgan]})"


def compose_doyoon_p8_timing(
    *,
    user_name: str,
    ilgan: str,
    raw_months: list[dict[str, Any]],
    start_year: int,
    start_month: int,
) -> dict[str, object]:
    """도윤 P-8 5-1 12개월 합성. 연우 P-8과 동일 데이터 + 도윤 텍스트."""
    if not user_name:
        raise ValueError("doyoon P-8 requires non-empty user_name")
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if len(raw_months) != 12:
        raise ValueError(f"raw_months 길이 12 필요. got {len(raw_months)}")

    peak_1_idx, peak_2_idx = _pick_top_two_peaks(raw_months)

    months_out: list[dict[str, object]] = []
    for i, m in enumerate(raw_months):
        pct = int(m["romanceScore"])
        is_first = i == peak_1_idx
        is_second = i == peak_2_idx
        is_peak = is_first or is_second
        hearts = 5 if is_peak else _pct_to_hearts_p8(pct)
        state = _classify_state(i, hearts, is_first, peak_2_idx, peak_1_idx)
        desc = STATE_DESC_BY_STATE_DOYOON.get(state, STATE_DESC_BY_STATE_DOYOON["상승"])
        label = _format_month_label(i, start_year, start_month)
        months_out.append({
            "label": label,
            "hearts": hearts,
            "pct": pct,
            "state": state,
            "desc": desc,
            "is_peak": is_peak,
        })

    peak_1_label = _peak_label_for_ai(peak_1_idx, start_year, start_month)
    peak_2_label = _peak_label_for_ai(peak_2_idx, start_year, start_month)

    ai_intro = "\n\n".join([
        PARA_1_FIXED_DOYOON,
        PARA_2_TEMPLATE_DOYOON.format(peak_1=peak_1_label, peak_2=peak_2_label),
        ILGAN_FLOW_BY_ILGAN_DOYOON[ilgan].format(
            ilgan_with_hanja=_ilgan_with_hanja_doyoon(ilgan)
        ),
    ])

    return {
        "months": months_out,
        "ai_intro": ai_intro,
        "bubble": BUBBLE_DOYOON,
        "peak_1_label": peak_1_label,
        "peak_2_label": peak_2_label,
    }


def get_doyoon_p8_facts(
    *,
    user_name: str,
    ilgan: str,
    raw_months: list[dict[str, Any]],
    start_year: int,
    start_month: int,
) -> dict[str, str]:
    """AI prompt용 facts."""
    composed = compose_doyoon_p8_timing(
        user_name=user_name, ilgan=ilgan,
        raw_months=raw_months,
        start_year=start_year, start_month=start_month,
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "peak_1_label": str(composed["peak_1_label"]),
        "peak_2_label": str(composed["peak_2_label"]),
        "rule_text": str(composed["ai_intro"]),
    }
