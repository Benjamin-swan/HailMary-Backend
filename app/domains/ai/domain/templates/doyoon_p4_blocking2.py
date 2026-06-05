"""도윤 P-4 二 연애를 막는 것 (2/2) — 룰 합성 + facts.

2-3 비호환 유형 (ai_akyon) + 2-4 착각 인연 (ai_illusion).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p4_data import (
    ACCURACY_MULTIPLIER,
    DECISIVE_GRADIENT_LABEL,
    DOYOON_AKYON_BY_SLOT,
    DOYOON_P4_DATA,
    FAKE_DROP_PCT,
    REAL_GROWTH_PCT,
    VALID_DOYOON_P4_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-4 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P4_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def _resolve_akyon(akyon_slot_id: str):
    return DOYOON_AKYON_BY_SLOT.get(akyon_slot_id) or DOYOON_AKYON_BY_SLOT["m-water-yang"]


def compose_doyoon_p4_akyon(
    *,
    user_name: str,
    ilgan: str,
    akyon_slot_id: str,
) -> str:
    """2-3 비호환 ai_akyon 합성 (350~450자, 3단락)."""
    _validate(user_name, ilgan)
    a = _resolve_akyon(akyon_slot_id)
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        f"데이터로 추려본, 잘 안 맞는 유형이에요. 외형부터 보여드릴게요.\n\n"
        f"키 분포는 평균보다 +5cm 이상인 경우가 {a.height_distribution_pct}. "
        "체형은 마른 골격에 어깨가 좁은 편이 많아요. 얼굴은 광대가 도드라지고 턱선이 각진 편. "
        f"눈매는 끝이 올라가고 입술이 얇은 모습이 비슷한 유형의 {a.common_signal_pct}에서 함께 보여요.\n\n"
        f"문제는 외형이 아니라 인상 점수예요. 첫인상 강도 {a.impression_first}점 — 눈에 띄게 높아요. "
        f"근데 6개월 호감 유지율이 {a.impression_6m}점. 격차가 {a.impression_gap}점이에요. "
        "평균 격차가 32점인 걸 감안하면 이 유형은 정말 조심하셔야 해요.\n\n"
        f"{ilgan}({ilgan_hanja}) 일간과는 감정의 결이 잘 안 맞는 편이에요. "
        "초기에 끌려도 중반 이후엔 금세 식기 쉬워요. "
        f"첫 만남에서 위 신호가 두 개 이상 보이면, 그냥 거리 두시는 게 나아요. "
        f"{user_name}님 매력을 낭비하기엔 아까운 유형이에요."
    )


def compose_doyoon_p4_illusion(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """2-4 착각 인연 ai_illusion 합성 (350~400자, 4단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P4_DATA[ilgan]
    s1, s2, s3 = d.illusion_signs
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        f"{ilgan}({ilgan_hanja}) 일간은 착각 인연에 빠지는 경우가 유독 잦은 편이에요. "
        "초기의 강한 끌림을 운명으로 오해하는 흐름이 자주 보이거든요.\n\n"
        f"핵심은 첫 만남 점수가 아니라 {DECISIVE_GRADIENT_LABEL}예요. "
        f"진짜 인연은 3개월 시점에 호감도가 {REAL_GROWTH_PCT} 올라가요. "
        f"착각 인연은 같은 시점에 {FAKE_DROP_PCT} 떨어지고요. "
        f"이 기울기 차이가 첫 만남 점수보다 훨씬 잘 들어맞는 신호예요.\n\n"
        f"오인 신호 3종 — {s1.keyword}, {s2.keyword}, "
        f"{s3.keyword}. 두 가지 이상 보이면 한 번 더 확인하고 가세요.\n\n"
        f"{user_name}님, 첫 만남 점수에 휘둘리지 마세요. 3개월 기다려 보는 게 가장 정확한 확인법이에요."
    )


# ── facts 추출 ────────────────────────────────────────────────────


def get_doyoon_p4_akyon_facts(
    *,
    user_name: str,
    ilgan: str,
    akyon_slot_id: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    a = _resolve_akyon(akyon_slot_id)
    rule_text = compose_doyoon_p4_akyon(
        user_name=user_name, ilgan=ilgan, akyon_slot_id=akyon_slot_id
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "height_distribution_pct": a.height_distribution_pct,
        "impression_first": a.impression_first,
        "impression_6m": a.impression_6m,
        "impression_gap": a.impression_gap,
        "emotional_volatility_multiplier": a.emotional_volatility_multiplier,
        "common_signal_pct": a.common_signal_pct,
        "rule_text": rule_text,
    }


def get_doyoon_p4_illusion_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P4_DATA[ilgan]
    rule_text = compose_doyoon_p4_illusion(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "illusion_multiplier": d.illusion_multiplier,
        "sign_1_keyword": d.illusion_signs[0].keyword,
        "sign_1_pct": d.illusion_signs[0].pct,
        "sign_2_keyword": d.illusion_signs[1].keyword,
        "sign_2_pct": d.illusion_signs[1].pct,
        "sign_3_keyword": d.illusion_signs[2].keyword,
        "sign_3_pct": d.illusion_signs[2].pct,
        "real_growth_pct": REAL_GROWTH_PCT,
        "fake_drop_pct": FAKE_DROP_PCT,
        "accuracy_multiplier": ACCURACY_MULTIPLIER,
        "rule_text": rule_text,
    }
