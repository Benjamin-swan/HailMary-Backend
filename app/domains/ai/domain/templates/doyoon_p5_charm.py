"""도윤 P-5 三 매력 분석 — 룰 합성 + facts (3 박스).

3-1 매력 지수 (charm_index) + 3-2 전환율 (conversion) + 3-3 호감 유발 (appeal).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p5_data import (
    CONVERSION_STEPS,
    DOYOON_P5_DATA,
    VALID_DOYOON_P5_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-5 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P5_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def compose_doyoon_p5_charm_index(
    *,
    user_name: str,
    ilgan: str,
    charm_pct: int,
) -> str:
    """3-1 매력 지수 ai_charm_index 합성 (300~350자, 3단락).

    Args:
        charm_pct: 상위 N% (정수, 1~99)
    """
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]

    return (
        f"상위 {charm_pct}%예요. 이거 그냥 숫자가 아니에요.\n\n"
        f"여섯 가지 매력 중에서 특히 빛나는 게 두 가지예요. {d.strength_axis_1}과 {d.strength_axis_2} — "
        "둘 다 또래 분들 사이에서도 유난히 두드러져요. 같은 일간을 가진 분들 중에서도 "
        "이 두 가지가 이만큼 살아 있는 분은 흔하지 않아요. 나머지 매력들도 평균은 충분히 넘고요. "
        "약한 데가 있는 게 아니라, 강한 데가 또렷한 분이에요.\n\n"
        f"다만 {user_name}님은 이걸 아직 제대로 안 쓰고 있어요. "
        "평소 무심코 새어 나올 때보다 마음먹고 보여줄 때 훨씬 더 환하게 살아나거든요. "
        "이 정도 매력이면, 조금만 의식해도 주변 반응이 꽤 달라질 거예요."
    )


def compose_doyoon_p5_conversion(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """3-2 전환율 ai_conversion 합성 (200~250자, 3단락)."""
    _validate(user_name, ilgan)
    s1, _s2, _s3, s4 = CONVERSION_STEPS

    return (
        f"첫인상 {s1[1]}%에서 시작해서 끌림 {s4[1]}%까지 이어지는 흐름이에요. "
        "처음 만난 순간부터 마음이 가까워지기까지 네 단계로 천천히 올라가요.\n\n"
        f"근데 재미있는 건, {user_name}님은 두 번째 만남에서 호감이 부쩍 깊어진다는 거예요. "
        "즉 한 번 만나고 끝내면 진짜 매력의 절반도 못 보여주는 거예요. "
        "첫 만남에서 멈춘 사람과 두 번째까지 이어간 사람의 호감 차이가 눈에 띄게 벌어지거든요.\n\n"
        f"첫 만남에서 두 번째 약속을 자연스럽게 만들어두세요. {user_name}님한테는 그게 가장 잘 맞는 방법이에요."
    )


def compose_doyoon_p5_appeal(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """3-3 호감 유발 ai_appeal 합성 (250~300자, 3단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    m1, m2, m3, m4 = d.appeal_meters

    return (
        "당신의 매력을 이루는 네 가지 모습을 짚어드릴게요.\n\n"
        f"{m1.name} {m1.value}, {m2.name} {m2.value}, {m3.name} {m3.value}, {m4.name} {m4.value}. "
        "특히 빛나는 두 가지와 아직 덜 드러난 두 가지가 또렷해요.\n\n"
        f"{d.weakness_axis_1}과 {d.weakness_axis_2}이 아직 덜 드러난 쪽이에요. "
        f"그런데 이건 {user_name}님이 마음만 먹으면 가장 쉽게 챙길 수 있는 부분이기도 해요. "
        "이 두 가지를 조금만 살리면 호감이 한결 또렷하게 전해져요. "
        "이미 강한 데를 더 키우기보다, 덜 드러난 데를 살피는 쪽이 훨씬 빠르게 와닿아요."
    )


# ── facts 추출 ────────────────────────────────────────────────────


def get_doyoon_p5_charm_index_facts(
    *,
    user_name: str,
    ilgan: str,
    charm_pct: int,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    rule_text = compose_doyoon_p5_charm_index(
        user_name=user_name, ilgan=ilgan, charm_pct=charm_pct
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "charm_pct": f"{charm_pct}%",
        "strength_axis_1": d.strength_axis_1,
        "strength_axis_2": d.strength_axis_2,
        "strength_multiplier": d.strength_multiplier,
        "conscious_gap_multiplier": d.conscious_gap_multiplier,
        "rule_text": rule_text,
    }


def get_doyoon_p5_conversion_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    rule_text = compose_doyoon_p5_conversion(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "step_1_pct": f"{CONVERSION_STEPS[0][1]}%",
        "step_2_pct": f"{CONVERSION_STEPS[1][1]}%",
        "step_3_pct": f"{CONVERSION_STEPS[2][1]}%",
        "step_4_pct": f"{CONVERSION_STEPS[3][1]}%",
        "second_meeting_multiplier": d.second_meeting_multiplier,
        "final_gap_pct": d.final_gap_pct,
        "rule_text": rule_text,
    }


def get_doyoon_p5_appeal_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    m1, m2, m3, m4 = d.appeal_meters
    rule_text = compose_doyoon_p5_appeal(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "meter_1_name": m1.name,
        "meter_1_value": str(m1.value),
        "meter_2_name": m2.name,
        "meter_2_value": str(m2.value),
        "meter_3_name": m3.name,
        "meter_3_value": str(m3.value),
        "meter_4_name": m4.name,
        "meter_4_value": str(m4.value),
        "weakness_axis_1": d.weakness_axis_1,
        "weakness_axis_2": d.weakness_axis_2,
        "appeal_boost_pct": d.appeal_boost_pct,
        "rule_text": rule_text,
    }


# ILGAN_HANJA re-export for downstream
__all__ = [
    "compose_doyoon_p5_charm_index",
    "compose_doyoon_p5_conversion",
    "compose_doyoon_p5_appeal",
    "get_doyoon_p5_charm_index_facts",
    "get_doyoon_p5_conversion_facts",
    "get_doyoon_p5_appeal_facts",
    "ILGAN_HANJA",
]
