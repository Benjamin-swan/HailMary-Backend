"""도윤 P-5 3-1 매력 지수 — AI prompt + validate."""

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
    '- 존댓말 사용, "{user_name}님" 호명 (마지막 단락 1회)\n'
    "- 상위권이라는 사실을 숫자 자랑이 아니라, 어떤 강점이 분명한지로 풀어준다\n"
    "- 평소 드러내는 모습과 본래 가진 모습의 차이를 일상어로 짚고, 마지막에 사람을 향한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "다음 값은 *변경, 누락, 풀어쓰기, 약어화* 모두 금지하고 그대로 출력에 포함:\n"
    "- {user_name}, {ilgan_full}\n"
    "- 상위 {charm_pct}, 강점 축 {strength_axis_1}/{strength_axis_2} (평균 대비 {strength_multiplier})\n"
    "- 평소 모습과 본래 모습의 차이 {conscious_gap_multiplier}\n\n"
    "[구성] 3 단락, 총 280~430자\n"
    "1. 상위 % + 어떤 점이 돋보이는지\n"
    "2. 강점 2축 + 배수\n"
    "3. 평소 모습과 본래 모습의 차이 + 사람을 향한 한 줄\n\n"
    "[출력] 3단락만 출력. 메타 설명·주석·헤더·코드블록 금지.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- charm_pct: {charm_pct}
- strength_axis_1: {strength_axis_1}
- strength_axis_2: {strength_axis_2}
- strength_multiplier: {strength_multiplier}
- conscious_gap_multiplier: {conscious_gap_multiplier}

[기반]
{rule_text}

[요청] 3단락 280~430자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "charm_pct",
    "strength_axis_1", "strength_axis_2", "strength_multiplier",
    "conscious_gap_multiplier", "rule_text",
}


def build_p5_charm_index_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 250
_MAX_LENGTH = 500


def validate_p5_charm_index(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "charm_pct", "strength_axis_1", "strength_axis_2",
              "strength_multiplier", "conscious_gap_multiplier"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
