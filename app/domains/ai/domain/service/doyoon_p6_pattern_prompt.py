"""도윤 P-6 4-2 행동 패턴 — AI prompt + validate."""

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
    '- 존댓말 사용, "{user_name}님" 호명 (마지막 단락에서 1회)\n'
    "- 연락하는 방식, 답장하는 모습, 마음이 흔들리거나 멀어지려 하는 순간을"
    " 반복되는 행동 패턴으로 짚어준다 — 마음 상태는 단정하지 말고"
    " '그런 마음이 드는 편이에요'처럼 조심스럽게 풀어준다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n\n"
    "[사실값 보존]\n"
    "- {user_name}, {ilgan_full}\n"
    "- 답장 길이 {answer_length_multiplier}\n"
    "- 망설이는 정도 {hesitation_pct}, 마음을 접고 싶어지는 정도 {cut_intent_pct}\n"
    "- 다시 풀릴 가능성 {resolution_pct}\n"
    "- {user_name}님이 먼저 다가설 때 잘 맞는 정도 {initiative_multiplier}\n\n"
    "[구성] 4단락, 총 280~440자\n"
    "1. 도입\n"
    "2. 연락하는 빈도와 답장하는 모습\n"
    "3. 망설이거나 멀어지려는 마음의 흐름\n"
    "4. 관계를 이어가는 방법 + {user_name}님 호명\n\n"
    "[출력] 4단락만.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- answer_length_multiplier: {answer_length_multiplier}
- hesitation_pct: {hesitation_pct}
- cut_intent_pct: {cut_intent_pct}
- resolution_pct: {resolution_pct}
- initiative_multiplier: {initiative_multiplier}

[기반]
{rule_text}

[요청] 4단락 280~440자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "answer_length_multiplier", "hesitation_pct", "cut_intent_pct",
    "resolution_pct", "initiative_multiplier", "rule_text",
}


def build_p6_pattern_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 240
_MAX_LENGTH = 500


def validate_p6_pattern(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "hesitation_pct", "cut_intent_pct", "resolution_pct"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
