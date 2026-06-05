"""도윤 P-5 3-3 호감 유발 — AI prompt + validate."""

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
    '- 존댓말 사용, "{user_name}님" 호명 (단락 2~3에서)\n'
    "- 네 가지 점수를 나열만 하지 말고, 무엇이 두드러지고 무엇이 아쉬운지 일상어로 짚어준다\n"
    "- 마지막은 사람을 향한 차분한 조언 한 줄로 마무리한다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "다음 값은 *변경, 누락, 풀어쓰기, 약어화* 모두 금지하고 그대로 출력에 포함:\n"
    "- {user_name}, {ilgan_full}\n"
    "- 네 가지 점수 ({meter_1_name} {meter_1_value} / {meter_2_name} {meter_2_value} /\n"
    "  {meter_3_name} {meter_3_value} / {meter_4_name} {meter_4_value})\n"
    "- 아쉬운 축 2개 ({weakness_axis_1} / {weakness_axis_2})\n"
    "- 호감 상승 폭 ({appeal_boost_pct})\n\n"
    "[구성] 3 단락, 총 220~380자\n"
    "1. 네 가지 점수 정리\n"
    "2. 잘 드러나는 점과 아쉬운 점\n"
    "3. 아쉬운 축을 보완하면 좋아지는 흐름 + 조언\n\n"
    "[출력] 3단락만 출력. 메타 설명·주석·헤더·코드블록 금지.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- meter_1: {meter_1_name} {meter_1_value}
- meter_2: {meter_2_name} {meter_2_value}
- meter_3: {meter_3_name} {meter_3_value}
- meter_4: {meter_4_name} {meter_4_value}
- weakness_axis_1: {weakness_axis_1}
- weakness_axis_2: {weakness_axis_2}
- appeal_boost_pct: {appeal_boost_pct}

[기반]
{rule_text}

[요청] 3단락 220~380자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "meter_1_name", "meter_1_value",
    "meter_2_name", "meter_2_value",
    "meter_3_name", "meter_3_value",
    "meter_4_name", "meter_4_value",
    "weakness_axis_1", "weakness_axis_2", "appeal_boost_pct", "rule_text",
}


def build_p5_appeal_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 450


def validate_p5_appeal(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    # 4 변수 이름 + 점수 모두 포함
    for k in ("meter_1_name", "meter_2_name", "meter_3_name", "meter_4_name",
              "meter_1_value", "meter_2_value", "meter_3_value", "meter_4_value",
              "weakness_axis_1", "weakness_axis_2", "appeal_boost_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
