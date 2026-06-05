"""도윤 P-1 1-1 Ch1 오프닝 — 4단락 350~400자 합성.

HTML 도윤_final.html line 1992~1999 임수 더미 톤 미러:
- 단락 1 (~80자): 호명 + 상위 N% 시그널 + 분류 케이스 명시
- 단락 2 (~100자): 일간 분포 % + love_type 세분화 + 일주 추가 가이드
- 단락 3 (~120자): 출력 비율·자기조절 등 분석적 진단 (어휘 다양화)
- 단락 4 (~70자): 최적화 가이드 한 가지 (작은 표현·주 N회 류)

일간 10셀별로 변형해 250조합 폭은 아니지만 충분한 다양성 확보.
어휘: 분류, 케이스, 구간, 발화, 출력 비율 — P-0과 다른 결.
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
)

# 일간별 "단락 3" 진단 본문 (~100~120자)
# 어휘: 처리량/출력, 진폭, 도달 구간, 발화 빈도 등 P-1 시그니처
ILGAN_DIAGNOSIS: dict[str, str] = {
    "갑목": (
        "특징은 — 결정은 빠른데 한 번 정하면 잘 안 바꾸는 편이에요. "
        "고른 다음에 다시 살피는 일이 드물고, 가던 길을 바꾸는 경우도 적은 편이에요."
    ),
    "을목": (
        "특징은 — 상대 분위기에 맞춰 결을 휘는데, 그게 쌓이면 자기 마음이 흐려져요. "
        "스스로를 드러내는 일이 적은 편이고, 맞추고 난 뒤에 회복은 조금 느린 편이에요."
    ),
    "병화": (
        "특징은 — 마음이 빨리 달아오르는데 그 열기가 오래가진 않아요. 평소보다 표현은 활발한데, "
        "한 사람에게 꾸준히 머무는 시간은 다소 짧은 편이에요."
    ),
    "정화": (
        "특징은 — 한 사람한테 깊이 들어가는 편이라 겉으로 표현은 잔잔하지만, "
        "한 사람을 두고 곱씹는 생각은 깊어요. 마음을 여는 데 시간이 걸리는 편이에요."
    ),
    "무토": (
        "특징은 — 마음의 변화 폭이 좁아 잔잔한 편이에요. 안정적이라는 뜻인데, "
        "초반 속도가 느려서 상대가 신호를 못 잡고 멀어지는 경우가 쌓이곤 해요."
    ),
    "기토": (
        "특징은 — 받쳐주는 데 강한데 정작 자기 자신은 뒤로 미루는 편이에요. "
        "마음을 많이 쏟는 만큼 스스로 지치는 속도도 평소보다 빠른 편입니다."
    ),
    "경금": (
        "특징은 — 판단이 또렷한 편인데, 부드럽게 전하는 표현은 적은 편이에요. "
        "방향은 분명한데 그걸 전하는 과정에서 거리감이 생기는 경우가 있어요."
    ),
    "신금": (
        "특징은 — 매력은 또렷하게 드러나는데 첫 마음을 여는 데까지는 시간이 좀 걸려요. "
        "관심이 들어와도 먼저 자신을 지킬 수 있는지부터 살피는 편이에요."
    ),
    "임수": (
        "특징을 정리하면 — 마음의 깊이는 있는데 표현이 그만큼 따라가질 않아요. "
        "속으로 생각은 많이 하시는데, 밖으로 꺼내 보이는 건 평소보다 한참 적은 편이에요."
    ),
    "계수": (
        "특징은 — 작은 부분까지 섬세하게 알아채는데, 그걸 드러내 말하는 일은 적은 편이에요. "
        "속에 담아둔 신호는 많은데 상대가 그걸 읽어줘야 하는 편이라, 사람에 따라 결과 차이가 큽니다."
    ),
}


# 일간별 "단락 4" 최적화 가이드 (~50~70자)
ILGAN_OPTIMIZATION: dict[str, str] = {
    "갑목": (
        "딱 하나만 권해드릴게요. 결정 전 30초 점검 한 번만 끼우시면, "
        "장기 관계 안정성이 꽤 올라가요."
    ),
    "을목": (
        "권해드리는 건 하나예요. 주 1회 자기 신호 한 줄만 표현하시면, "
        "관계 안에서의 자기 위치가 분명해져요."
    ),
    "병화": (
        "권해드릴 건 단순해요. 텐션 한 단계 낮춰서 주 1회만 잔잔한 대화를 만드시면, "
        "관계 지속성이 다르게 올라가요."
    ),
    "정화": (
        "한 가지만 권해드릴게요. 초반 30일에 작은 신호 주 2회만 의식적으로 노출하시면, "
        "진입 시간이 꽤 단축됩니다."
    ),
    "무토": (
        "권해드리는 건 하나예요. 작은 변화의 신호를 주 1회만 더 보여주시면, "
        "상대가 마음을 알아채는 속도가 한결 빨라져요."
    ),
    "기토": (
        "딱 하나만 권해드릴게요. 내가 원하는 것 한 가지를 분명히 말로 표현하시면, "
        "오래 가는 관계에서 균형이 다시 잡힙니다."
    ),
    "경금": (
        "한 가지만 권해드릴게요. 솔직한 말을 꺼내기 전에 한 줄 부드러운 말만 덧붙이시면, "
        "마음이 훨씬 잘 전해져요."
    ),
    "신금": (
        "권해드릴 건 단순해요. 첫 마음을 여는 신호를 주 1회만 먼저 보내시면, "
        "가까워지는 속도가 한결 빨라집니다."
    ),
    "임수": (
        "딱 하나만 바꿔보세요. 표현 빈도를 주 1회만 의식적으로 늘려보시면, "
        "주변에서 {USER_NAME}님을 읽는 방식이 꽤 달라질 거예요."
    ),
    "계수": (
        "권해드리는 건 하나예요. 속에 담아둔 마음을 주 1회만 말로 옮겨 보시면, "
        "잘 맞는 사람을 만날 가능성이 단번에 올라가요."
    ),
}


def compose_doyoon_p1_opening(
    *,
    user_name: str,
    ilgan: str,
    ilju: str,
) -> str:
    """1-1 Ch1 오프닝 합성. 350~400자 범위 출력.

    Args:
        user_name: User.name (호명)
        ilgan: 일간 한글 (예: "임수")
        ilju: 일주 한자 표기 (예: "임술(壬戌)")

    Returns:
        4단락 합성 텍스트 (단락 사이 \\n\\n).

    Raises:
        ValueError: user_name 빈 문자열
        KeyError: 알 수 없는 일간
    """
    if not user_name:
        raise ValueError("doyoon P-1 opening requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]

    para1 = (
        f"솔직히 말씀드릴게요. {user_name}님은 상위 {data.pct_value}%에 드는 분이에요. "
        f"그냥 듣기 좋으라고 드리는 말이 아니에요. 같은 일간 안에서 이런 결이 이렇게 또렷하게 보이는 일이 흔치 않거든요."
    )

    para2 = (
        f"{ilgan} 일간 중에서도 '{data.love_type}'에 해당하는 분은 흔치 않아요. "
        f"여기에 {ilju} 일주까지 더하면 결이 한층 더 또렷해집니다."
    )

    para3 = ILGAN_DIAGNOSIS[ilgan]

    para4 = ILGAN_OPTIMIZATION[ilgan].replace("{USER_NAME}", user_name)

    return "\n\n".join([para1, para2, para3, para4])


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p1_opening_facts(
    *,
    user_name: str,
    ilgan: str,
    ilju_hanja: str,
) -> dict[str, str]:
    """P-1 ai_opening AI prompt에 박을 사실값 + 룰 합성 텍스트.

    Args:
        user_name: 사용자 이름 (호명)
        ilgan: 일간 한글 (예: "임수")
        ilju_hanja: 한자 표기 일주 (예: "임술(壬戌)") — application layer가 미리 변환

    Returns:
        사실값 dict + rule_text. AI가 모두 보존해야 함.

    Raises:
        ValueError / KeyError: 입력 가드 실패.
    """
    if not user_name:
        raise ValueError("doyoon P-1 opening facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]
    rule_text = compose_doyoon_p1_opening(
        user_name=user_name, ilgan=ilgan, ilju=ilju_hanja
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "ilju_hanja": ilju_hanja,
        "love_type": data.love_type,
        "pct_value": f"{data.pct_value}%",
        "ilgan_diagnosis_text": ILGAN_DIAGNOSIS[ilgan],
        "ilgan_optimization_text": ILGAN_OPTIMIZATION[ilgan].replace(
            "{USER_NAME}", user_name
        ),
        "rule_text": rule_text,
    }
