"""도윤 P-1 1-3 감정 곡선 — AI prompt builder + validate.

3단락 230~350자. 차트 그래프 보조 톤. user_name은 룰 본문에 없어 검증 X.
"""

from __future__ import annotations

from app.domains.ai.domain.service.doyoon_tone_guide import (
    DOYOON_FORBIDDEN_BLOCK,
    DOYOON_TONE_GUIDE,
)

# 공유 톤 블록은 placeholder({})가 없어 .format() 안전 — 문자열 결합으로 삽입.
_SYSTEM_PROMPT = (
    "당신은 도화선 서비스의 캐릭터 한도윤입니다. "
    "한도윤은 사주 데이터를 사람의 언어로 풀어주는 상담가형 분석가입니다.\n\n"
    + DOYOON_TONE_GUIDE + "\n\n"
    "[페르소나]\n"
    "- 존댓말 (호명 선택적, 강제 X — 감정 흐름을 짚어주는 차분한 톤)\n"
    "- 감정이 크게 출렁이는 때와 가라앉으며 회복되는 때를 자연스럽게 풀어준다\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 분석 끝에 사람을 향한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 일간 ({ilgan_full})\n"
    "- 힘든 시기의 흔들림 정도 ({crisis_pct})\n"
    "- 회복되는 정도 ({recovery_pct})\n"
    "- 마음을 표현했을 때의 효과 ({expression_effect_pct})\n"
    "출력 텍스트에 위 문자열들이 그대로 포함돼야 합니다.\n\n"
    "[구성] 3 단락, 단락 사이 빈 줄 1개, 총 210~380자\n"
    "1. 도입 — 힘든 시기 {crisis_pct} + 흔들림이 {crisis_multiplier} 커진다는 점 + 회복 {recovery_pct} (2~3문장)\n"
    "2. {ilgan_full} 일간의 감정이 흐르는 특성 (2문장)\n"
    "3. 마음을 솔직히 표현하는 작은 습관 + 그 효과 {expression_effect_pct} (2~3문장)\n\n"
    "[출력] 3단락 텍스트만. 메타 설명·헤더·코드블록 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-1 감정 곡선 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- ilgan_full: {ilgan_full}
- crisis_pct: {crisis_pct}
- recovery_pct: {recovery_pct}
- crisis_multiplier: {crisis_multiplier}
- expression_effect_pct: {expression_effect_pct}

[참고 — 일간 감정 곡선 진단 본문]
{curve_diag_text}

[룰 합성 기반 텍스트 — 이걸 *기반으로* 같은 사실값을 모두 보존한 채 표현을 다양화하세요. \
그대로 복붙 금지. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값을 모두 포함하는 3단락 210~380자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "crisis_pct",
    "recovery_pct",
    "crisis_multiplier",
    "expression_effect_pct",
    "curve_diag_text",
    "rule_text",
}


def build_p1_emotion_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")

    system = _SYSTEM_PROMPT.format(
        ilgan_full=facts["ilgan_full"],
        crisis_pct=facts["crisis_pct"],
        recovery_pct=facts["recovery_pct"],
        crisis_multiplier=facts["crisis_multiplier"],
        expression_effect_pct=facts["expression_effect_pct"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 190
_MAX_LENGTH = 450


def validate_p1_emotion(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    """user_name 검증 X (룰 본문에 없음 — AI 출력에 들어가도 안 들어가도 OK)."""
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"

    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["crisis_pct"] not in text:
        return False, f"crisis_pct missing: {facts['crisis_pct']!r}"
    if facts["recovery_pct"] not in text:
        return False, f"recovery_pct missing: {facts['recovery_pct']!r}"
    if facts["expression_effect_pct"] not in text:
        return False, "expression_effect_pct missing"

    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks} breaks (expected 2)"

    return True, ""
