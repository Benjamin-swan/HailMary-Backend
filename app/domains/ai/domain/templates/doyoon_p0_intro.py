"""도윤 P-0 0-5 분석 진입 요약 — 4단락 템플릿 합성 + AI facts 추출.

사용자 결정 (PAID_GUIDE_DOYOON.md):
- 룰 합성은 **AI 호출 fallback** 역할로 유지 (이전엔 메인 합성 경로).
- 메인 경로는 generate_p0_diagnosis_usecase가 AI 호출 → 검증 실패 시 본 모듈로 fallback.

데이터 구조 (단일 진실원):
- ILGAN_HANJA: 일간 한글 → 한자 매핑 (10셀)
- OHANG_HANJA: 오행 한글 → 한자 (5셀)
- OHANG_EXCESS_INTENSITY: 과다 강도 정성어 (5셀, 셀마다 다른 어휘)
- OHANG_LACK_INTENSITY: 부족 강도 정성어 (5셀)
- OHANG_EXCESS_IMPACT: excess별 과다 작용 메커니즘 1문장 (5셀)

기존 PARA_3A/3B/IMPACT는 위 dict에서 *합성*돼 생성 — 동일 텍스트 출력 보장
(테스트 호환). 정량 정책(2026-06-05 결정): 오행 5원소에 "상위 N%" 백분위는 근거가
없어 폐기 — 접촉률 등 모든 수치 통계를 질적 강도 표현으로 대체.
"""

from __future__ import annotations

PARA_1_OPENING_TPL = "{user_name}님, 데이터 정리 다 끝났어요."


# ── 매핑 dict (단일 진실원) ──────────────────────────────────────

ILGAN_HANJA: dict[str, str] = {
    "갑목": "甲木", "을목": "乙木",
    "병화": "丙火", "정화": "丁火",
    "무토": "戊土", "기토": "己土",
    "경금": "庚金", "신금": "辛金",
    "임수": "壬水", "계수": "癸水",
}

OHANG_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}

# 백분위 수치 폐기(2026-06-05). 오행 5원소에 "상위 N%" percentile은 근거가 없어
# 질적 강도 표현으로 대체. 셀마다 다른 어휘 (템플릿 어휘 다양화).
# 문장: "{오행}({한자}) 기운이 {강도} 과다한 상태고,"
OHANG_EXCESS_INTENSITY: dict[str, str] = {
    "목": "도드라지게",
    "화": "뚜렷하게",
    "토": "두텁게",
    "금": "강하게",
    "수": "넘치도록",
}

# 부족 강도 정성어 (5종). 문장: "{오행}({한자}) 기운은 {강도} 부족한 것으로 나타나요."
OHANG_LACK_INTENSITY: dict[str, str] = {
    "목": "현저히",
    "화": "확연히",
    "토": "눈에 띄게",
    "금": "두드러지게",
    "수": "심하게",
}


# ── 일간 강점 문구 (단락 2) ─────────────────────────────────────

# QA C1/Z: 배수("평균 대비 1.x배") 제거 → 비수치 정성 표현. 셀마다 다른 어휘(다양화).
ILGAN_PARA_2: dict[str, str] = {
    "갑목": (
        "일간은 갑목(甲木) — 의사결정 속도와 신념 일관성이 또렷하게 높은 편인 유형이에요. "
        "방향을 정해 밀고 가는 힘도 같은 일간 가운데 도드라지는 편이에요."
    ),
    "을목": (
        "일간은 을목(乙木) — 적응 속도와 환경 수용도가 유연하게 높은 편인 유형이에요. "
        "상대에 맞춰 변하는 폭도 같은 일간 가운데 넓은 편이에요."
    ),
    "병화": (
        "일간은 병화(丙火) — 표현 빈도와 에너지 노출도가 뚜렷하게 높은 편인 유형이에요. "
        "첫인상의 강도도 같은 일간 가운데 강하게 나타나는 편이에요."
    ),
    "정화": (
        "일간은 정화(丁火) — 한 사람에게 집중하는 깊이가 진하게 나타나는 유형이에요. "
        "오래 이어가는 힘도 같은 일간 가운데 단단한 편이에요."
    ),
    "무토": (
        "일간은 무토(戊土) — 안정감과 신뢰가 쌓이는 속도가 꾸준히 높은 편인 유형이에요. "
        "관계의 일관성도 같은 일간 가운데 안정적인 편이에요."
    ),
    "기토": (
        "일간은 기토(己土) — 받아주는 폭과 헌신의 빈도가 넉넉하게 높은 편인 유형이에요. "
        "상대의 성장을 돕는 힘도 같은 일간 가운데 두드러지는 편이에요."
    ),
    "경금": (
        "일간은 경금(庚金) — 판단의 명확성과 결단 속도가 분명하게 높은 편인 유형이에요. "
        "흐트러진 걸 정리하는 힘도 같은 일간 가운데 또렷한 편이에요."
    ),
    "신금": (
        "일간은 신금(辛金) — 매력의 드러남과 정서의 깊이가 섬세하게 높은 편인 유형이에요. "
        "끌어당기는 힘도 같은 일간 가운데 돋보이는 편이에요."
    ),
    "임수": (
        "일간은 임수(壬水) — 깊이감과 통찰력이 남다르게 높은 편인 유형이에요. "
        "사람을 끄는 매력도 같은 일간 가운데 은근히 강한 편이에요."
    ),
    "계수": (
        "일간은 계수(癸水) — 섬세함과 환경 적응이 부드럽게 높은 편인 유형이에요. "
        "작은 디테일을 잡아내는 힘도 같은 일간 가운데 예민한 편이에요."
    ),
}


# ── 단락 3 합성 (위 dict에서 생성, 단일 진실원) ──────────────────

OHANG_EXCESS_PARA_3A: dict[str, str] = {
    oh: f"다만 오행 분포에서 {oh}({OHANG_HANJA[oh]}) 기운이 {OHANG_EXCESS_INTENSITY[oh]} 과다한 상태고,"
    for oh in OHANG_HANJA
}

OHANG_LACK_PARA_3B: dict[str, str] = {
    oh: (
        f"{oh}({OHANG_HANJA[oh]}) 기운은 {OHANG_LACK_INTENSITY[oh]} 부족한 것으로 나타나요. "
        "이 두 변수가 연애 영역에서 직접적인 영향을 줘요."
    )
    for oh in OHANG_HANJA
}

# 과다 오행별 작용 메커니즘 1문장 (수치 없이 질적). 셀마다 다른 어휘.
OHANG_EXCESS_IMPACT: dict[str, str] = {
    "목": "木이 과하면 추진력은 세지지만, 속도를 조절하지 못해 관계가 버거워지는 지점이 생겨요.",
    "화": "火가 넘치면 감정 표현은 빠르고 강해지지만, 그 흐름을 안정적으로 이어가는 힘이 약해지는 지점이 생겨요.",
    "토": "土가 두터우면 안정감은 크지만, 변화에 둔해져 관계가 정체되는 지점이 생겨요.",
    "금": "金이 강하면 판단은 또렷하지만, 날카로움이 앞서 상대가 움츠러드는 지점이 생겨요.",
    "수": "水가 넘치면 공감의 폭은 넓지만, 감정에 깊이 잠겨 거리 조절이 어려워지는 지점이 생겨요.",
}


PARA_4_CLOSING = "다음 장부터 이 변수들을 하나씩 분석해드릴게요. 그냥 따라오시면 돼요."


VALID_DOYOON_P0_ILGAN: frozenset[str] = frozenset(ILGAN_PARA_2.keys())
VALID_DOYOON_P0_OHANG: frozenset[str] = frozenset(OHANG_HANJA.keys())


# ── 합성 함수 (룰 fallback) ──────────────────────────────────────


def compose_doyoon_p0_intro(
    *,
    user_name: str,
    ilgan: str,
    ohang_excess: str,
    ohang_lack: str,
) -> str:
    """4단락 도윤 톤 합성. 220~300자 범위 출력.

    AI 호출 실패·검증 실패 시 fallback 경로로 호출됨.

    Args:
        user_name: 사용자 이름 (User.name). 단락 1 호명에 박힘.
        ilgan: 일간 한글 (갑목/을목/.../계수 10종)
        ohang_excess: 과다 오행 한글 (목/화/토/금/수)
        ohang_lack: 부족 오행 한글

    Returns:
        4단락 합성 텍스트 (단락 사이 \\n\\n).

    Raises:
        ValueError: user_name 빈 문자열
        KeyError: 알 수 없는 일간 또는 오행
    """
    if not user_name:
        raise ValueError("doyoon P-0 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P0_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if ohang_excess not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_excess: {ohang_excess!r}")
    if ohang_lack not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_lack: {ohang_lack!r}")

    para_3 = " ".join([
        OHANG_EXCESS_PARA_3A[ohang_excess],
        OHANG_LACK_PARA_3B[ohang_lack],
        OHANG_EXCESS_IMPACT[ohang_excess],
    ])

    return "\n\n".join([
        PARA_1_OPENING_TPL.format(user_name=user_name),
        ILGAN_PARA_2[ilgan],
        para_3,
        PARA_4_CLOSING,
    ])


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p0_facts(
    *,
    user_name: str,
    ilgan: str,
    ohang_excess: str,
    ohang_lack: str,
) -> dict[str, str]:
    """AI prompt에 substituted 박을 사실값 + 출력 검증에 쓸 keys.

    AI는 이 사실값들을 *변경/누락 없이* 그대로 출력에 포함해야 함.
    검증 함수가 각 값이 AI 출력에 포함됐는지 verify.

    Returns:
        키 9개:
            user_name, ilgan_full, ilgan_hanja,
            excess_ohang, excess_ohang_hanja,
            lack_ohang, lack_ohang_hanja,
            ilgan_para_2 (참고용 룰 합성 일간 강점 문구),
            rule_text (전체 룰 합성 결과 — AI variation 기반)

    Raises:
        ValueError / KeyError: compose와 동일 가드.
    """
    if not user_name:
        raise ValueError("doyoon P-0 facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P0_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if ohang_excess not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_excess: {ohang_excess!r}")
    if ohang_lack not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_lack: {ohang_lack!r}")

    rule_text = compose_doyoon_p0_intro(
        user_name=user_name,
        ilgan=ilgan,
        ohang_excess=ohang_excess,
        ohang_lack=ohang_lack,
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "excess_ohang": ohang_excess,
        "excess_ohang_hanja": OHANG_HANJA[ohang_excess],
        "lack_ohang": ohang_lack,
        "lack_ohang_hanja": OHANG_HANJA[ohang_lack],
        "ilgan_para_2": ILGAN_PARA_2[ilgan],
        "rule_text": rule_text,
    }
