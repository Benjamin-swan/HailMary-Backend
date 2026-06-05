"""도윤 P-3 二 연애를 막는 것 (1/2) — 룰 합성 + facts.

2-1 구조적 원인 (ai_blockade) + 2-2 반복 패턴 (ai_pattern).
원본 도윤_final.html data-page-idx=3 구조 정합.
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p3_data import (
    BLOCKADE_BY_OHANG,
    DOYOON_P3_DATA,
    VALID_DOYOON_P3_ILGAN,
    VALID_DOYOON_P3_OHANG,
)


def _validate(user_name: str, ilgan: str, ohang_excess: str | None = None) -> None:
    if not user_name:
        raise ValueError("doyoon P-3 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P3_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if ohang_excess is not None and ohang_excess not in VALID_DOYOON_P3_OHANG:
        raise KeyError(f"unknown ohang_excess: {ohang_excess!r}")


def compose_doyoon_p3_blockade(
    *,
    user_name: str,
    ilgan: str,
    ohang_excess: str,
) -> str:
    """2-1 구조적 원인 ai_blockade 합성 (300~350자, 3단락)."""
    _validate(user_name, ilgan, ohang_excess)
    b = BLOCKADE_BY_OHANG[ohang_excess]

    return (
        f"먼저 흐름부터 짚어드릴게요. {user_name}님의 사주를 보면 {ohang_excess}({b.ohang_hanja}) "
        f"기운이 {b.blockade_multiplier} 강하게 나타나요. 잠깐 강한 정도가 아니라 깊게 쌓여 있는 상태예요.\n\n"
        f"이게 새 인연이 들어올 자리를 좁혀요. 같은 기운이 이미 가득 차 있으면 비슷한 결의 사람이 들어설 틈이 줄어들거든요. "
        f"같은 일간을 가진 분들 중에서도 {ohang_excess}({b.ohang_hanja})가 강한 경우엔 새 인연이 닿는 흐름이 "
        f"눈에 띄게 더디게 나타나요. 우연이 아니에요.\n\n"
        f"방법은 의외로 단순해요. 비우는 거예요. 사람이든 미련이든 답 안 오는 연락이든 — 하나만 정리해도 "
        f"새 인연이 들어올 자리가 다시 열려요. 새로 더하기보다 묵은 걸 덜어내는 쪽이 훨씬 가벼워지는 길이에요."
    )


def compose_doyoon_p3_pattern(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """2-2 반복 패턴 ai_pattern 합성 (250~300자, 4단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P3_DATA[ilgan]
    p1, p2, p3 = d.patterns

    return (
        f"{user_name}님이 연애에서 되풀이하는 흐름을 3단계로 나눠봤어요.\n\n"
        f"1단계 — {p1.keyword} (자주 나타남 {p1.pct}). {p1.desc}\n\n"
        f"2단계 — {p2.keyword} (자주 나타남 {p2.pct}). {p2.desc}\n\n"
        f"3단계 — {p3.keyword} (자주 나타남 {p3.pct}). {p3.desc} "
        f"{ilgan} 일간이 흔히 보이는 흐름이에요. 다음 관계에서 1단계 속도만 조금 늦춰도 "
        "관계가 한결 더 안정적으로 자리잡을 수 있어요. 마음을 숨기라는 게 아니라, "
        "한 박자 여유를 두는 것만으로 흐름이 꽤 달라진다는 뜻이에요."
    )


# ── facts 추출 ────────────────────────────────────────────────────


def get_doyoon_p3_blockade_facts(
    *,
    user_name: str,
    ilgan: str,
    ohang_excess: str,
) -> dict[str, str]:
    _validate(user_name, ilgan, ohang_excess)
    b = BLOCKADE_BY_OHANG[ohang_excess]
    rule_text = compose_doyoon_p3_blockade(
        user_name=user_name, ilgan=ilgan, ohang_excess=ohang_excess
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "ohang_excess": ohang_excess,
        "ohang_excess_hanja": b.ohang_hanja,
        "blockade_pct": b.blockade_pct,
        "blockade_multiplier": b.blockade_multiplier,
        "rule_text": rule_text,
    }


def get_doyoon_p3_pattern_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P3_DATA[ilgan]
    rule_text = compose_doyoon_p3_pattern(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "pattern_1_keyword": d.patterns[0].keyword,
        "pattern_1_pct": d.patterns[0].pct,
        "pattern_2_keyword": d.patterns[1].keyword,
        "pattern_2_pct": d.patterns[1].pct,
        "pattern_3_keyword": d.patterns[2].keyword,
        "pattern_3_pct": d.patterns[2].pct,
        "rule_text": rule_text,
    }
