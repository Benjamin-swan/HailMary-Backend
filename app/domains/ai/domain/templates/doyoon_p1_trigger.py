"""도윤 P-1 1-2 트리거 발화 메커니즘 — 2단락 200~250자 합성.

HTML 도윤_final.html line 2042~2047 임수 더미 톤 미러:
- 단락 1 (~80자): 3 트리거 순차로 겹치면 흐름이 거의 정해진다는 의미 (수치 미언급)
- 단락 2 (~140자): 처음 30일 + 트리거 1+2 결합 + 속도 조절 어려운 이유 (수치 미언급)

어휘: 발화, 도달 확률, 자기조절, 임계점 — P-1 시그니처. P-0의 "분포"와 다른 결.
"""

from __future__ import annotations

from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
)

# 일간별 단락 2 추가 진단 (~50자) — 자기조절 어려운 이유 한 줄
ILGAN_CONTROL_REASON: dict[str, str] = {
    "갑목": "한 번 방향이 정해지면 다시 살피는 일이 줄어들기 때문이에요.",
    "을목": "분위기에 맞추다 보면 자기 마음이 흐려지는 일이 자꾸 쌓이거든요.",
    "병화": "한 번 마음이 달아오르면 속도를 늦추기가 어려운 편이라서요.",
    "정화": "한 사람한테 들어가면 그 사람 생각을 오래 곱씹게 되거든요.",
    "무토": "차분한 편이라 초반엔 더딘데, 한 번 마음을 주면 빠져나오기 어려워요.",
    "기토": "받쳐주는 마음이 커지면 정작 자기 자신을 자꾸 뒤로 미루게 돼요.",
    "경금": "방향이 또렷해지면 그쪽으로 단호하게 가는 편이라 그래요.",
    "신금": "마음을 끄는 신호가 들어오면 스스로를 지킬 수 있는지부터 살피며 깊어져요.",
    "임수": "생각이 많은 편이라 한 번 빠지면 거기서 헤어 나오는 데 시간이 더 걸려요.",
    "계수": "잔잔한 신호가 쌓이면 겉으로 드러나지 않은 채 마음이 깊어지거든요.",
}


def compose_doyoon_p1_trigger(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """1-2 트리거 메커니즘 합성. 200~250자.

    Args:
        user_name: User.name
        ilgan: 일간 한글
    """
    if not user_name:
        raise ValueError("doyoon P-1 trigger requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]

    para1 = (
        "흥미로운 부분이에요. 마음을 흔드는 신호 세 가지가 차례로 겹치는 순간, "
        "그 흐름이 그대로 이어지는 경우가 대부분이에요. 사실상 방향이 잡혔다고 봐도 될 만큼이죠."
    )

    para2 = (
        f"특히 처음 30일 안에 '{data.trigger_1}'과 '{data.trigger_2}'가 같이 찾아오면, "
        f"{ilgan} 일간인 {user_name}님은 그때부터 스스로 속도를 늦추기가 쉽지 않아요. "
        f"{ILGAN_CONTROL_REASON[ilgan]} 그래서 신호가 겹치기 시작하는 시점을 "
        "미리 알아두는 게 생각보다 많이 달라질 수 있어요."
    )

    return "\n\n".join([para1, para2])


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


# 초기 진입 시간 — 일간 무관 고정 표기.
PEAK_WINDOW_DAYS = "30일"


def get_doyoon_p1_trigger_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """P-1 ai_trigger AI prompt에 박을 사실값 + 룰 합성 텍스트.

    Returns:
        사실값 dict + rule_text. AI가 모두 보존해야 함.
        검증 핵심: user_name, ilgan, trigger_1/2, 30일 (수치 %는 제거).

    Raises:
        ValueError / KeyError: 입력 가드 실패.
    """
    if not user_name:
        raise ValueError("doyoon P-1 trigger facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]
    rule_text = compose_doyoon_p1_trigger(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "trigger_1": data.trigger_1,
        "trigger_2": data.trigger_2,
        "trigger_3": data.trigger_3,
        "peak_window_days": PEAK_WINDOW_DAYS,
        "control_reason_text": ILGAN_CONTROL_REASON[ilgan],
        "rule_text": rule_text,
    }
