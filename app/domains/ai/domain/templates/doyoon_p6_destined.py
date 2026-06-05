"""도윤 P-6 四 운명의 짝 (1/2) — 룰 합성 + facts (3 박스)."""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import (
    ILGAN_HANJA,
    OHANG_HANJA,
)
from app.domains.ai.domain.value_object.doyoon_p6_data import (
    DOYOON_INYON_BY_SLOT,
    DOYOON_P6_DATA,
    VALID_DOYOON_P6_ILGAN,
    DoyoonInyonData,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-6 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P6_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def _resolve_inyon(match_slot_id: str) -> DoyoonInyonData:
    return DOYOON_INYON_BY_SLOT.get(match_slot_id) or DOYOON_INYON_BY_SLOT["f-water-yang"]


def compose_doyoon_p6_profile(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
    pct_value: int,
    ohang_lack: str,
) -> str:
    """4-1 인연 프로파일 합성 (400~500자, 4단락)."""
    _validate(user_name, ilgan)
    i = _resolve_inyon(match_slot_id)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    lack_hanja = OHANG_HANJA.get(ohang_lack, ohang_lack)

    return (
        f"궁합 지수 상위 {pct_value}%예요. 잘 맞는 인연의 모습부터 차분히 그려드릴게요.\n\n"
        f"외형부터 볼게요. 키는 평균 ±5cm 안쪽이 가장 많고, 체형은 균형 잡힌 골격에 어깨선이 단단한 편이에요. "
        "얼굴은 선이 부드러운 둥근형이 많고, 이마가 넓은 인상이 자주 보여요. "
        "눈매가 길고 끝이 부드럽게 떨어지는 인상이 특히 잘 어울려요.\n\n"
        "성격도 짚어드릴게요. 감정 기복이 크지 않고 마음이 차분하게 가라앉아 있는 사람이에요. "
        "그만큼 곁에 있으면 안정감이 또렷하게 느껴져요. "
        "직업은 기획·교육·창작 쪽에서 특히 잘 맞는 인연이 많아요.\n\n"
        f"무엇보다 {ohang_lack}({lack_hanja}) 기운을 채워주는 사람이라는 게 커요. "
        f"{user_name}님 사주에서 비어 있던 자리를 이 사람이 자연스럽게 메워주거든요. "
        f"{ilgan}({ilgan_hanja}) 일간과의 궁합이 {i.compatibility_pct}까지 올라가는 이유예요. "
        "평균보다 한참 위라고 보시면 돼요."
    )


def compose_doyoon_p6_meeting(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
) -> str:
    """4-1 만남 시나리오 합성 (300~400자, 3단락)."""
    _validate(user_name, ilgan)
    _resolve_inyon(match_slot_id)
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        "이 사람을 만나게 될 자리부터 짚어드릴게요. "
        "처음 가보는 곳보다, 이미 자주 다니는 동선 안에서 다시 마주칠 가능성이 훨씬 커요. "
        "새로운 곳을 찾기보다 늘 가던 자리를 챙기시는 게 좋아요.\n\n"
        "첫 만남은 짧고 평범한 대화로 시작될 거예요. 인상에 강하게 남지 않는 경우가 많아요. "
        "그래서 처음엔 알아채지 못하고 그냥 지나칠 수도 있어요. "
        "일부러 못 알아보는 게 아니라, 원래 그런 식으로 스며들 듯 다가오는 인연이에요.\n\n"
        "결정적인 건 두 번째 마주침이에요. 두 번째에 호감이 눈에 띄게 빠르게 올라가거든요. "
        f"{ilgan}({ilgan_hanja}) 일간을 가진 분들에게서 이 흐름이 한결같이 보여요. "
        f"{user_name}님, 첫 만남에서 두 번째 약속을 자연스럽게 잡아두시면 가장 좋아요."
    )


def compose_doyoon_p6_pattern(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """4-2 행동 패턴 합성 (300~350자, 4단락)."""
    _validate(user_name, ilgan)
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        "그 사람의 행동을 하나씩 읽어드릴게요.\n\n"
        "연락을 보면 — 답장은 길게 잘 해주는데, 먼저 연락은 잘 안 하는 사람이에요. "
        "이걸 보통 '관심 없나 보다'로 받아들이기 쉬운데, 정말 관심이 없으면 답장부터 짧고 무심해져요. "
        "길게 답해준다는 건 그만큼 마음을 쓰고 있다는 뜻이에요. 그저 먼저 다가서는 게 서툰 사람일 뿐이에요.\n\n"
        "마음 상태를 들여다보면 — 망설임은 큰데 끊어낼 생각은 거의 없어요. "
        "끝낼 마음은 없는데, 아직 시작할 용기를 못 낸 상태라고 보시면 돼요.\n\n"
        f"{ilgan}({ilgan_hanja}) 일간을 가진 분들을 보면, 이런 어정쩡한 사이는 "
        "둘 중 한 사람이 작은 신호만 보내도 의외로 쉽게 풀려요. "
        f"그러니 {user_name}님이 먼저 가볍게 손 내미는 쪽이 한결 잘 풀릴 가능성이 높아요."
    )


# ── facts 추출 ────────────────────────────────────────────────────


def get_doyoon_p6_profile_facts(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
    pct_value: int,
    ohang_lack: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    i = _resolve_inyon(match_slot_id)
    rule_text = compose_doyoon_p6_profile(
        user_name=user_name, ilgan=ilgan, match_slot_id=match_slot_id,
        pct_value=pct_value, ohang_lack=ohang_lack,
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "ohang_lack": ohang_lack,
        "ohang_lack_hanja": OHANG_HANJA.get(ohang_lack, ohang_lack),
        "pct_value": f"{pct_value}%",
        "height_distribution_pct": i.height_distribution_pct,
        "profile_signal_pct": i.profile_signal_pct,
        "emotional_stability_multiplier": i.emotional_stability_multiplier,
        "stability_high_multiplier": i.stability_high_multiplier,
        "compatibility_pct": i.compatibility_pct,
        "avg_compatibility_baseline": i.avg_compatibility_baseline,
        "compatibility_lift": i.compatibility_lift,
        "rule_text": rule_text,
    }


def get_doyoon_p6_meeting_facts(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    i = _resolve_inyon(match_slot_id)
    rule_text = compose_doyoon_p6_meeting(
        user_name=user_name, ilgan=ilgan, match_slot_id=match_slot_id
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "existing_path_multiplier": i.existing_path_multiplier,
        "low_impact_pct": i.low_impact_pct,
        "second_contact_multiplier": i.second_contact_multiplier,
        "rule_text": rule_text,
    }


def get_doyoon_p6_pattern_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P6_DATA[ilgan]
    rule_text = compose_doyoon_p6_pattern(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "answer_length_multiplier": d.answer_length_multiplier,
        "hesitation_pct": d.hesitation_pct,
        "cut_intent_pct": d.cut_intent_pct,
        "resolution_pct": d.resolution_pct,
        "initiative_multiplier": d.initiative_multiplier,
        "rule_text": rule_text,
    }
