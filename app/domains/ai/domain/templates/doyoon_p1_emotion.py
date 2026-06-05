"""도윤 P-1 1-3 감정 강도 분석 — 3단락 250~300자 합성.

HTML 도윤_final.html line 2085~2089 임수 더미 톤 미러:
- 단락 1 (~70자): 위기 % + 평균 대비 1.X배 + 회복 % 평이성
- 단락 2 (~100자): {ILGAN} 일간 특성 — 초반 차분 → 폭발 패턴
- 단락 3 (~80자): 작은 표현 효과 N% + 마무리

어휘: 진폭, 폭발 강도, 회복 곡선, 의식적 노출 — P-1 시그니처. 차트 보조 톤.
"""

from __future__ import annotations

from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
)

# 일간별 단락 2 진단 (~80~100자) — 감정 곡선 특성
ILGAN_CURVE_DIAG: dict[str, str] = {
    "갑목": (
        "{ILGAN} 일간이 원래 이래요. 한 번 방향을 정하면 끝까지 밀고 가는데, "
        "힘든 시기엔 다른 사람의 말을 받아들이기가 평소보다 어려워지는 편이에요."
    ),
    "을목": (
        "{ILGAN} 일간이 그래요. 상대 분위기에 맞춰 결을 휘다가 힘든 시기에 참았던 마음이 한꺼번에 터지곤 해요. "
        "가라앉을 때쯤 또 분위기에 맞춰 휘어 들어가는 일이 반복돼요."
    ),
    "병화": (
        "{ILGAN} 일간이 원래 이래요. 마음이 빨리 달아올라 힘든 시기로 들어가는 것도 빠른 편이고, "
        "다행히 가라앉고 회복하는 것도 다른 일간보다 빠른 편이긴 해요."
    ),
    "정화": (
        "{ILGAN} 일간이 그래요. 한 사람한테 깊이 집중하다가 힘든 시기에 마음이 한꺼번에 크게 흔들리곤 해요. "
        "회복도 한참 깊은 곳에서 시작하는 편이라 시간이 걸려요."
    ),
    "무토": (
        "{ILGAN} 일간이 원래 차분해요. 마음의 흔들림이 작은 편이라 힘든 시기도 비교적 덜 출렁이는데, "
        "회복이 빠르진 않아서 한 자리에 오래 머무는 편이에요."
    ),
    "기토": (
        "{ILGAN} 일간이 그래요. 받쳐주는 마음이 커서 평소엔 잔잔한데, "
        "힘든 시기에 한 번 참았던 마음이 터지면 가라앉는 데 평소보다 더 걸려요."
    ),
    "경금": (
        "{ILGAN} 일간이 원래 이래요. 판단이 또렷한 편이라 힘든 시기엔 마음이 날카로워지고, "
        "회복은 비교적 빠른데 그 사이 관계를 끊는 결정이 빠르게 나오는 편이에요."
    ),
    "신금": (
        "{ILGAN} 일간이 그래요. 자신을 지키려는 마음이 커서 힘든 시기엔 크게 흔들리고, "
        "회복은 빠른 편인데 마음을 다시 여는 데까지는 시간이 더 걸려요."
    ),
    "임수": (
        "{ILGAN} 일간이 원래 이래요. 처음엔 무척 차분해 보이다가 어느 순간 마음이 한꺼번에 쏟아지곤 해요. "
        "가라앉아 회복하는 시기도 평소보다 깊고 길어요."
    ),
    "계수": (
        "{ILGAN} 일간이 그래요. 잔잔한 흔들림이 쌓이다 힘든 시기에 한꺼번에 겉으로 드러나는 편이에요. "
        "회복은 다시 스며들듯 천천히 이뤄지고요."
    ),
}


def compose_doyoon_p1_emotion(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """1-3 감정 곡선 분석 합성. 250~300자.

    Args:
        user_name: User.name
        ilgan: 일간 한글
    """
    if not user_name:
        raise ValueError("doyoon P-1 emotion requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]
    crisis_pct = data.emotion_curve[2]  # 위기 %
    recovery_pct = data.emotion_curve[3]  # 회복 %

    para1 = (
        f"그래프 보시면 느끼시겠지만, 힘든 시기에 마음이 {crisis_pct}%까지 출렁여요. "
        f"평소의 {data.crisis_multiplier} 정도예요. 회복도 {recovery_pct}% 수준에서 한참 머물러요."
    )

    para2 = ILGAN_CURVE_DIAG[ilgan].replace("{ILGAN}", ilgan)

    para3 = (
        f"마음을 미리 조금씩 꺼내두면 그 흔들림이 줄어요. 작은 표현이라도 주 2회 이상 꾸준히 해보시면 "
        f"힘든 시기의 흔들림이 {data.expression_effect_pct}%만큼 잦아들어요. 어렵게 생각하지 마시고, "
        f"그냥 작은 표현을 자주 하시면 돼요."
    )

    return "\n\n".join([para1, para2, para3])


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p1_emotion_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """P-1 ai_emotion AI prompt에 박을 사실값 + 룰 합성 텍스트.

    Returns:
        사실값 dict + rule_text. AI가 모두 보존해야 함.
        검증 핵심: ilgan, crisis_pct, recovery_pct, crisis_multiplier, expression_effect_pct.
        user_name은 본 박스 룰에 안 들어가서 검증 생략 (선택적 포함).

    Raises:
        ValueError / KeyError: 입력 가드 실패.
    """
    if not user_name:
        raise ValueError("doyoon P-1 emotion facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]
    rule_text = compose_doyoon_p1_emotion(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "crisis_pct": f"{data.emotion_curve[2]}%",
        "recovery_pct": f"{data.emotion_curve[3]}%",
        "crisis_multiplier": data.crisis_multiplier,
        "expression_effect_pct": f"{data.expression_effect_pct}%",
        "curve_diag_text": ILGAN_CURVE_DIAG[ilgan].replace("{ILGAN}", ilgan),
        "rule_text": rule_text,
    }
