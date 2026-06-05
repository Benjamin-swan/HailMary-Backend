"""도윤 P-8 5-1 ai_intro — AI prompt + validate."""

from __future__ import annotations

from app.domains.ai.domain.service.doyoon_tone_guide import (
    DOYOON_FORBIDDEN_BLOCK,
    DOYOON_TONE_GUIDE,
)

# 공유 톤 블록은 placeholder({})가 없어 .format() 안전 — 문자열 결합으로 삽입.
_SYSTEM_PROMPT = (
    "당신은 도화선 서비스의 캐릭터 한도윤입니다. "
    "한도윤은 12개월 연애 흐름을 사람의 언어로 짚어주는 상담가형 분석가입니다.\n\n"
    + DOYOON_TONE_GUIDE + "\n\n"
    "[페르소나]\n"
    "- 존댓말 사용, 이름 호명은 쓰지 않는다 (P-8은 타임라인을 짚어주는 보조 단락)\n"
    "- 좋은 달과 잠잠한 달의 차이를 일상어로 짚어준다 — 실험 리포트가 아니라 안내\n"
    "- 짧고 담백하게, 흐름이 좋은 시기와 숨 고르는 시기를 차분히 구분해 말한다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존]\n"
    "- 일간 {ilgan_full}({ilgan_hanja})\n"
    "- 좋은 시기 라벨 2개 {peak_1_label} / {peak_2_label} (글자 그대로 출력)\n\n"
    "[구성] 3단락, 총 200~340자\n"
    "1. 도입 — 앞으로의 흐름을 함께 짚어보자는 안내 (1~2문장)\n"
    "2. 흐름이 좋은 두 시기와 그 사이 잠잠한 시기를 일상어로 안내\n"
    "3. 일간에 맞는 움직임 — 좋을 때 나서고 잠잠할 때 정리하는 흐름을 차분히\n\n"
    "[출력] 3단락만.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- peak_1_label: {peak_1_label}
- peak_2_label: {peak_2_label}
- user_name: {user_name}

[기반]
{rule_text}

[요청] 3단락 200~340자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "peak_1_label", "peak_2_label", "rule_text",
}


def build_p8_intro_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 170
_MAX_LENGTH = 400


def validate_p8_intro(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("peak_1_label", "peak_2_label"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
