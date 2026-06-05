"""도윤 P-10 box1/box2 — facts 빌더 + 룰 fallback.

원본 도윤_final.html data-page-idx=10 편지 박스.
연우는 BOX1/BOX2 매트릭스 룰 합성 — 도윤은 AI 호출 (도윤 톤).
AI 실패 시 룰 fallback (이 모듈의 compose_* 함수).

옵션별 답 데이터 (페이지 언급 X, 사실값 직접 인용):
- step1/step2 각 옵션이 답해질 사주 데이터를 정적 매트릭스(P-3·P-5·P-6)에서 추출.
- timing 슬러그는 동적 peak_labels (P-8 raw_months 기반) 인수로 받음.
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import (
    ILGAN_HANJA,
    OHANG_HANJA,
)
from app.domains.ai.domain.value_object.doyoon_p3_data import DOYOON_P3_DATA
from app.domains.ai.domain.value_object.doyoon_p4_data import DOYOON_P4_DATA
from app.domains.ai.domain.value_object.doyoon_p5_data import DOYOON_P5_DATA
from app.domains.ai.domain.value_object.doyoon_p6_data import DOYOON_P6_DATA

STEP1_LABEL: dict[str, str] = {
    "waiting_new": "새로운 인연을 기다리는 상태",
    "crushing": "썸 진행 중",
    "in_relationship": "연애 중",
    "missing_ex": "헤어진 연인을 그리워하는 상태",
}

STEP2_LABEL: dict[str, str] = {
    "soulmate": "운명의 상대",
    "timing": "다음 인연의 시기",
    "compatibility": "현재 인연과의 궁합",
    "patterns": "연애 패턴의 본질",
}


# 편지 섹션 수치 비표기 정책(2026-06-05): % / 점 같은 숫자는 딱딱해서 정성 강도어로 대체.
# 단 '다음 인연 시기'의 월(月)은 데이터라 예외로 그대로 둠.
def _score_level(score: int) -> str:
    """0~100 점수/지표를 정성 강도어로 변환."""
    if score >= 80:
        return "뚜렷하게 높은"
    if score >= 65:
        return "높은"
    if score >= 50:
        return "보통 수준의"
    return "낮은"


# ── 옵션별 답 데이터 빌더 ─────────────────────────────────────────


def _build_step1_answer_block(
    ilgan: str,
    slug: str,
    peak_labels: tuple[str, str] | None,
) -> str:
    """step1 슬러그 1개의 답 사실값 한 줄. 페이지 라벨 언급 X."""
    p3 = DOYOON_P3_DATA.get(ilgan)
    p4 = DOYOON_P4_DATA.get(ilgan)
    p5 = DOYOON_P5_DATA.get(ilgan)
    p6 = DOYOON_P6_DATA.get(ilgan)

    if slug == "crushing" and p5:
        return (
            f"썸 진행 중: 매력 강점 두 가지({p5.strength_axis_1}·{p5.strength_axis_2})가 "
            "평소보다 두드러지게 측정. "
            "두 번째 만남에서 호감 전환율이 한결 더 올라가는 흐름."
        )
    if slug == "in_relationship" and p6:
        return (
            f"연애 중: 상대 관심도는 {_score_level(p6.interest_score)} 편이고, "
            f"표현 의지는 {_score_level(p6.expression_score)} 편, "
            f"지속 가능성은 {_score_level(p6.durability_score)} 편이에요. "
            "답장 길이가 평소보다 한결 더 길게 나타나는 패턴이고요."
        )
    if slug == "missing_ex" and p3 and p4:
        # 착각 신호는 P-4 데이터(키워드에 점수 포함)라 편지에선 숫자 떼고 정성 인용.
        p_pat = p3.patterns
        return (
            f"헤어진 연인: 반복 패턴 — '{p_pat[0].keyword}', '{p_pat[1].keyword}' 같은 "
            "흐름이 자주 나타나는 편. 착각 인연 발생률이 평소보다 두드러지게 높음 — "
            "첫인상을 유독 강하게 받아들이는 신호가 도드라지게 분포."
        )
    if slug == "waiting_new":
        if peak_labels:
            return (
                "새 인연 기다리는 상태: 향후 12개월 신규 접촉 확률이 평소보다 크게 "
                f"올라가는 시기는 {peak_labels[0]}과 {peak_labels[1]}."
            )
        return (
            "새 인연 기다리는 상태: 향후 12개월 동안 신규 접촉 확률이 평소보다 "
            "크게 올라가는 피크 구간이 두 곳 측정됨."
        )
    return f"{STEP1_LABEL.get(slug, slug)}: 데이터 분석 진행 중."


def _build_step2_answer_block(
    ilgan: str,
    slug: str,
    peak_labels: tuple[str, str] | None,
) -> str:
    """step2 슬러그 1개의 답 사실값 한 줄. 페이지 라벨 언급 X."""
    p3 = DOYOON_P3_DATA.get(ilgan)
    p6 = DOYOON_P6_DATA.get(ilgan)

    if slug == "soulmate":
        # 일간 무관 공통 fallback 데이터 (f-water-yang 베이스)
        return (
            "운명의 상대: 인연 프로파일 — 따뜻한 인상·조용한 사람·표현 일관성. "
            "감정 변동성이 평소보다 한결 안정적. 궁합 지수가 평균을 훨씬 웃도는 수준으로 측정됨."
        )
    if slug == "timing":
        if peak_labels:
            return (
                f"다음 인연 시기: {peak_labels[0]}과 {peak_labels[1]}에 "
                "신규 접촉 확률이 평소보다 크게 상승. 그 사이 구간은 충전기."
            )
        return (
            "다음 인연 시기: 향후 12개월에 신규 접촉 확률이 평소보다 크게 "
            "올라가는 피크 구간이 두 차례 측정됨."
        )
    if slug == "compatibility" and p6:
        return (
            f"현재 궁합: 상대 관심도는 {_score_level(p6.interest_score)} 편, "
            f"표현은 {_score_level(p6.expression_score)} 편, "
            f"지속 가능성은 {_score_level(p6.durability_score)} 편. "
            "답장 길이가 평소보다 한결 더 긴 편 — 관심은 있되 망설이는 교착 패턴."
        )
    if slug == "patterns" and p3:
        p_pat = p3.patterns
        return (
            f"연애 패턴 본질: {p_pat[0].keyword} → {p_pat[1].keyword} → "
            f"{p_pat[2].keyword}. 구조적 변수가 단계적으로 누적되는 흐름."
        )
    return f"{STEP2_LABEL.get(slug, slug)}: 데이터 분석 진행 중."


def build_step1_answer_data(
    ilgan: str,
    step1: tuple[str, ...],
    peak_labels: tuple[str, str] | None = None,
) -> str:
    """선택한 step1 슬러그들의 답 데이터 합성 (한 블록당 한 줄)."""
    return "\n".join(_build_step1_answer_block(ilgan, s, peak_labels) for s in step1)


def build_step2_answer_data(
    ilgan: str,
    step2: tuple[str, ...],
    peak_labels: tuple[str, str] | None = None,
) -> str:
    """선택한 step2 슬러그들의 답 데이터 합성."""
    return "\n".join(_build_step2_answer_block(ilgan, s, peak_labels) for s in step2)


# ── 동적 글자수 계산 (옵션 수 기반) ───────────────────────────────


def calc_box_length_range(option_count: int, *, base_min: int, base_max: int) -> tuple[int, int]:
    """선택 옵션 수에 비례한 min/max 글자수. 옵션 1개 = base, 4개 = base의 약 2배 길이."""
    n = max(1, min(4, option_count))
    multiplier = 1.0 + (n - 1) * 0.33  # 1→1.0, 2→1.33, 3→1.66, 4→2.0
    return int(base_min * multiplier), int(base_max * multiplier)


# ── 룰 fallback (AI 실패 시) ──────────────────────────────────────


def compose_doyoon_box1_body(
    *,
    user_name: str,
    ilgan: str,
    step1: tuple[str, ...],
    peak_labels: tuple[str, str] | None = None,
) -> str:
    """도윤 box1 룰 합성 — 입력 상황 + 옵션별 답 데이터 직접 인용."""
    if not step1:
        raise ValueError("step1 required")
    labels = [STEP1_LABEL.get(s, s) for s in step1]
    labels_text = " · ".join(labels)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    answer_block = build_step1_answer_data(ilgan, step1, peak_labels)
    return (
        f"{user_name}님이 골라주신 지금 상황, 차근차근 정리해드릴게요.\n\n"
        f"입력해주신 건 {labels_text}예요. {ilgan}({ilgan_hanja}) 일간이신 분들에게서 "
        "이 조합은 비슷한 흐름으로 자주 보여요.\n\n"
        f"{answer_block}\n\n"
        f"{user_name}님, 지금 당장 무언가 결정하지 않으셔도 돼요. 먼저 차분히 살펴보고 그다음에 움직이셔도 늦지 않아요."
    )


def compose_doyoon_box2_body(
    *,
    user_name: str,
    ilgan: str,
    step2: tuple[str, ...],
    peak_labels: tuple[str, str] | None = None,
) -> str:
    """도윤 box2 룰 합성 — 알고싶은 영역의 답 데이터 직접 인용."""
    if not step2:
        raise ValueError("step2 required")
    labels = [STEP2_LABEL.get(s, s) for s in step2]
    labels_text = " · ".join(labels)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    answer_block = build_step2_answer_data(ilgan, step2, peak_labels)
    return (
        f"{user_name}님이 궁금하다고 표시해주신 부분, 지금 풀어서 보여드릴게요.\n\n"
        f"여쭤보신 건 {labels_text}예요. {ilgan}({ilgan_hanja}) 일간을 기준으로 정리하면 이렇게 보여요.\n\n"
        f"{answer_block}\n\n"
        f"{user_name}님, 지금 보여드릴 수 있는 부분까지는 최대한 또렷하게 짚어드린 거예요. "
        "지금 답할 수 있는 부분과 조금 더 지켜봐야 하는 부분은 분명하게 나뉘어요."
    )


# ── facts ─────────────────────────────────────────────────────────


def get_doyoon_box1_facts(
    *,
    user_name: str,
    ilgan: str,
    step1: tuple[str, ...],
    peak_labels: tuple[str, str] | None = None,
) -> dict[str, str]:
    if not user_name:
        raise ValueError("user_name required")
    if not step1:
        raise ValueError("step1 required")
    rule_text = compose_doyoon_box1_body(
        user_name=user_name, ilgan=ilgan, step1=step1, peak_labels=peak_labels
    )
    answer_data = build_step1_answer_data(ilgan, step1, peak_labels)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "step1_labels": " · ".join(STEP1_LABEL.get(s, s) for s in step1),
        "step1_count": str(len(step1)),
        "answer_data": answer_data,
        "rule_text": rule_text,
    }


def get_doyoon_box2_facts(
    *,
    user_name: str,
    ilgan: str,
    step2: tuple[str, ...],
    ohang_lack: str,
    peak_labels: tuple[str, str] | None = None,
) -> dict[str, str]:
    if not user_name:
        raise ValueError("user_name required")
    if not step2:
        raise ValueError("step2 required")
    rule_text = compose_doyoon_box2_body(
        user_name=user_name, ilgan=ilgan, step2=step2, peak_labels=peak_labels
    )
    answer_data = build_step2_answer_data(ilgan, step2, peak_labels)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "step2_labels": " · ".join(STEP2_LABEL.get(s, s) for s in step2),
        "step2_count": str(len(step2)),
        "ohang_lack": ohang_lack,
        "ohang_lack_hanja": OHANG_HANJA.get(ohang_lack, ohang_lack),
        "answer_data": answer_data,
        "rule_text": rule_text,
    }
