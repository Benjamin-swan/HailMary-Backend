"""도윤 P-7 四 운명의 짝 · 결말 (2/2) — 룰 합성 + facts (1 박스).

핵심 원칙 (2026-05-23 재설계):
- AI는 *카드 표 라벨 (소멸 65% / 좋은 결말 78% / 좋은 결말 91%)* 만 풀이.
- 별도 메타 수치 (sc1/2/3_six_month_pct, initiative_multiplier, wait_cost_multiplier,
  expected_value_ratio) — facts에서 제외. 카드 외 수치는 사용자가 확인 불가 → hallucination처럼 보임.
- 시나리오 우선순위: 시나리오 3 (91% 최고 수치, 단 조건부 대기) >
  시나리오 2 (78% 권장 능동 분기) > 시나리오 1 (65% 소멸).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p7_data import (
    DOYOON_P7_DATA,
    VALID_DOYOON_P7_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-7 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P7_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def compose_doyoon_p7_ending(*, user_name: str, ilgan: str) -> str:
    """4-3 결말 시나리오 ai_ending 합성 — 카드 풀이 톤 (380~560자, 5단락).

    카드 라벨 (65%/78%/91%)만 사용. 별도 메타 수치 X.
    """
    _validate(user_name, ilgan)
    _validate_ilgan_data(ilgan)
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        "세 갈래로 갈리는 결말, 카드로 정리해드렸어요.\n\n"
        "첫 번째 길 — 지금 이대로 두면 소멸 65%. "
        "양쪽 모두 멈춰 선 채로 마음이 천천히 식어가는 흐름이에요. "
        "가장 흔한 결말이지만 그만큼 멀어지기 쉬운 길입니다.\n\n"
        f"두 번째 길 — {user_name}님이 먼저 다가갈 때. 좋은 결말 78%. "
        f"제가 가장 권해드리고 싶은 길이에요. "
        f"{ilgan}({ilgan_hanja}) 성향을 가진 분들이 먼저 작은 신호를 보낼 때 잘 풀리는 흐름이거든요. "
        f"{user_name}님이 직접 정할 수 있다는 점이 가장 중요해요.\n\n"
        "세 번째 길 — 상대가 먼저 다가올 때. 좋은 결말 91% — 가능성 자체는 가장 높아요. "
        "다만 상대가 움직이기를 기다려야 하는 길이라, 그만큼 시간이 더 걸립니다.\n\n"
        f"{user_name}님, 결정은 온전히 본인 몫이에요. "
        f"다만 한 가지만 짚어드리면 — 78%는 {user_name}님이 지금 바로 움직일 수 있는 길이고, "
        "91%는 기다림 위에 놓인 길이에요. 저는 먼저 다가가는 쪽을 권해드릴게요."
    )


def _validate_ilgan_data(ilgan: str) -> None:
    """DOYOON_P7_DATA에 일간 존재 확인 (compose에서 d 접근은 빼고 카드 라벨만 사용)."""
    if ilgan not in DOYOON_P7_DATA:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def get_doyoon_p7_ending_facts(*, user_name: str, ilgan: str) -> dict[str, str]:
    """facts — 카드 라벨만 prompt에 노출.

    sc1/2/3_six_month_pct, initiative_multiplier, wait_cost_multiplier,
    expected_value_ratio 등 *카드에 없는 별도 메타 수치는 제외*.
    """
    _validate(user_name, ilgan)
    _validate_ilgan_data(ilgan)
    rule_text = compose_doyoon_p7_ending(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        # 카드 라벨 (모든 일간 동일 — _build_scenarios 공통)
        "sc1_label": "소멸 65%",
        "sc2_label": "좋은 결말 78%",
        "sc3_label": "좋은 결말 91%",
        "rule_text": rule_text,
    }
