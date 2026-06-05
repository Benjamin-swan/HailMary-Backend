"""도윤 P-6 4-1 만남 시나리오 — AI prompt + validate."""

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
    "- 어디서 어떻게 만나게 되는지, 첫 만남의 분위기, 다시 이어가는 방법을"
    " 일상어로 차분히 풀어준다 — 거리나 동선 이야기는 실험 데이터가 아니라"
    " 생활 장면처럼 묘사한다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n\n"
    "[사실값 보존]\n"
    "- {user_name}, {ilgan_full}\n"
    "- 기존 동선 {existing_path_multiplier}\n"
    "- 첫 만남에서 강한 인상으로 남을 확률 {low_impact_pct}\n"
    "- 두 번째 만남 {second_contact_multiplier}\n\n"
    "[구성] 3단락, 총 280~440자\n"
    "1. 어디서 어떤 분위기로 만나게 되는지\n"
    "2. 첫 만남에서 자연스럽게 나타나는 모습\n"
    "3. 다시 만남을 이어가는 방법 + {user_name}님 호명\n\n"
    "[출력] 3단락만.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- existing_path_multiplier: {existing_path_multiplier}
- low_impact_pct: {low_impact_pct}
- second_contact_multiplier: {second_contact_multiplier}

[기반]
{rule_text}

[요청] 3단락 280~440자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "existing_path_multiplier", "low_impact_pct", "second_contact_multiplier",
    "rule_text",
}


def build_p6_meeting_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 240
_MAX_LENGTH = 500


def validate_p6_meeting(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "low_impact_pct"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
