"""도윤 P-9 六 연애 변수 최적화 가이드 — 룰 합성 + facts (3 박스)."""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import (
    ILGAN_HANJA,
    OHANG_HANJA,
)
from app.domains.ai.domain.value_object.doyoon_p9_data import (
    DOYOON_P9_DATA,
    OHANG_BOOST_PCT,
    VALID_DOYOON_P9_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-9 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P9_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def compose_doyoon_p9_ohang(*, user_name: str, ilgan: str, ohang_lack: str) -> str:
    """6-1 오행 보완 ai_ohang 합성 — 카드 풀이 톤.

    별도 메타 수치 (반응성 배수·최대 부스트) 인용 X. 카드 라벨 (9%+7%+7%=23%)만 풀이.
    """
    _validate(user_name, ilgan)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    lack_hanja = OHANG_HANJA.get(ohang_lack, ohang_lack)

    return (
        f"{ilgan}({ilgan_hanja}) 일간 {user_name}님께 {ohang_lack}({lack_hanja})을 채워주는 방법을 카드로 정리해드렸어요. "
        f"세 가지를 함께 챙기시면 인연이 들어올 가능성이 평균 {OHANG_BOOST_PCT}만큼 높아져요.\n\n"
        "보완 방법 1(+9%) 색을 더하는 건 가장 가볍게 시작할 수 있어요. 옷차림 비율을 조금 늘리시는 정도면 돼요. "
        "방법 2(+7%) 방향을 가까이 두기와 방법 3(+7%) 몸으로 채우기는 시간을 두고 천천히 쌓이는 방법이에요.\n\n"
        f"세 가지를 30일쯤 이어가시면 23%의 변화가 차분히 자리 잡아요. "
        f"{user_name}님은 효과 +9%인 색 더하기부터 먼저 해보시길 권해드려요."
    )


def compose_doyoon_p9_risk(*, user_name: str, ilgan: str) -> str:
    """6-2 리스크 제거 ai_risk 합성 — 카드 풀이 톤.

    별도 메타 수치 (36% 임팩트) 인용 X. 카드 라벨 (81%·64%·47%)만 풀이.
    QA F-056: 위험도 % 단순 합산(192→130)은 통계적으로 무의미해 제거.
    """
    _validate(user_name, ilgan)
    return (
        "주의하면 좋을 카드 세 장을 정리해드렸어요. 즉시 81%가 가장 신경 쓰이는 부분이고, 단기 64%, 중기 47% 순서예요. "
        "위험도 숫자가 그대로 챙기는 순서를 알려줘요.\n\n"
        f"{user_name}님, 세 가지를 한꺼번에 다 신경 쓰실 필요는 없어요. "
        "즉시(81%)부터 하나씩 차근차근 정리하시는 게 가장 좋아요. 숫자 큰 것부터 위에서 아래로 차례대로 보시면 돼요."
    )


def compose_doyoon_p9_optimize(*, user_name: str, ilgan: str) -> str:
    """6-3 매력 최적화 ai_optimize 합성 (250~300자, 3단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P9_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]
    gap = d.target_score - d.current_score

    return (
        f"{d.current_score}에서 {d.target_score}까지 딱 {gap}점 남았어요. "
        "이 차이는 세 가지에서 생겨요 — 잠깐 멈추기, 시선 안정, 표현 빈도.\n\n"
        f"{ilgan}({ilgan_hanja}) 일간은 잠깐 멈추기 하나만 챙겨도 매력이 {d.gap_per_action}씩 살아나요. "
        "30일 의식해서 해보시면 6~8점은 올라요. "
        f"{d.target_score}점을 넘기면 호감을 사는 흐름이 {d.overall_boost_pct}만큼 좋아져요.\n\n"
        f"별거 없어요. 그냥 시작하시면 돼요. 분석은 다 끝났어요. 이제 공은 {user_name}님한테 있어요."
    )


# ── facts ─────────────────────────────────────────────────────────


def get_doyoon_p9_ohang_facts(*, user_name: str, ilgan: str, ohang_lack: str) -> dict[str, str]:
    """6-1 facts — *카드에 표시되는 사실값만* prompt에 노출.

    응답성 배수 (1.6배) / 최대 부스트 (28%) 같은 별도 메타 수치는 제외 —
    사용자가 표에서 확인할 수 없어 hallucination처럼 보임.
    """
    _validate(user_name, ilgan)
    rule_text = compose_doyoon_p9_ohang(user_name=user_name, ilgan=ilgan, ohang_lack=ohang_lack)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "ohang_lack": ohang_lack,
        "ohang_lack_hanja": OHANG_HANJA.get(ohang_lack, ohang_lack),
        "boost_pct": OHANG_BOOST_PCT,    # 카드 합산 (9+7+7)
        "rule_text": rule_text,
    }


def get_doyoon_p9_risk_facts(*, user_name: str, ilgan: str) -> dict[str, str]:
    """6-2 facts — *카드에 표시되는 사실값만* prompt에 노출.

    즉시 변수 단독 임팩트(36%)·위험도 단순 합산(192→130) 등 별도 메타 수치는 제외
    (QA F-056: 무의미한 합산).
    """
    _validate(user_name, ilgan)
    rule_text = compose_doyoon_p9_risk(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "rule_text": rule_text,
    }


def get_doyoon_p9_optimize_facts(*, user_name: str, ilgan: str) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P9_DATA[ilgan]
    rule_text = compose_doyoon_p9_optimize(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "current_score": str(d.current_score),
        "target_score": str(d.target_score),
        "gap_per_action": d.gap_per_action,
        "overall_boost_pct": d.overall_boost_pct,
        "rule_text": rule_text,
    }
