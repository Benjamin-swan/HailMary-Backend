"""도윤 P-2 1-5 회복 곡선 — 풀 템플릿 합성 + facts 추출 (원본 도윤 구조).

원본 meter × 4 (직후/1개월/3개월/6개월) + SD + 한도윤 버블.
AI 박스 = 평균 회복 곡선 분석 (감정 강도 잔여 기준) + 처방 (350~400자).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p2_data import (
    DOYOON_P2_DATA,
    VALID_DOYOON_P2_ILGAN,
)


def compose_doyoon_p2_recovery(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """1-5 회복 곡선 합성 — ai_recovery만 반환 (meters/bubble는 facts 노출)."""
    if not user_name:
        raise ValueError("doyoon P-2 recovery requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]

    # 단락2는 위 진행바(직후/1개월/3개월/6개월 %)와 중복되므로 수치 없이 문장으로만 (2026-06-05 결정).
    ai_recovery = (
        f"이별 후 마음이 어떻게 가라앉는지 정리해 드릴게요. "
        f"{ilgan}({ilgan_hanja}) 일간을 가진 분들의 평균적인 회복 흐름이에요.\n\n"
        "헤어진 직후엔 감정이 거의 그대로 남아 묵직하게 자리해요. "
        "한 달이 지나면 조금씩 천천히 가라앉기 시작하고, "
        "세 달쯤엔 한결 가벼워진 게 느껴져요. 여섯 달이 되면 대부분 옅어져 일상에 무리가 없을 만큼 정리됩니다.\n\n"
        f"평균 회복 곡선과 견주면 {data.recovery_lag_multiplier} 흘러가는 편이에요. "
        f"{user_name}님은 마음이 자연스럽게 가라앉기를 기다려 주는 게 가장 편안한 길입니다. "
        "억지로 잊으려 애쓰면 오히려 더 오래 머물러요.\n\n"
        "마음이 정리되기 전에 새 인연을 서두르면 부딪히기 쉬워요. "
        "충분히 비워낸 다음에 새 사람을 받아들이는 게 좋아요."
    )

    return {
        "ai_recovery": ai_recovery,
    }


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p2_recovery_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    if not user_name:
        raise ValueError("doyoon P-2 recovery facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    composed = compose_doyoon_p2_recovery(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "recovery_lag_multiplier": data.recovery_lag_multiplier,
        "rule_text": composed["ai_recovery"],
    }
