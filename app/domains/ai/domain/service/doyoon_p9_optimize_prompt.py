"""도윤 P-9 6-3 매력 최적화 — AI prompt + validate."""

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
    '- 존댓말 사용, "{user_name}님" 호명 (마지막 단락에서)\n'
    "- 현재와 목표 사이의 차이를 숫자로 통보하지 말고, 어디서 차이가 나는지 일상어로 짚어준다\n"
    "- 분석을 마친 뒤 등을 밀어주듯 따뜻하게 마무리하는 어조\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n\n"
    "[사실값 보존]\n"
    "- {user_name}, {ilgan_full}\n"
    "- 현재/목표 ({current_score}/{target_score})\n"
    "- 한 가지 실천당 상승폭 {gap_per_action}\n"
    "- 전체 상승폭 {overall_boost_pct}\n\n"
    "[구성] 3 단락, 총 220~340자\n"
    "1. 현재 점수와 목표 점수의 차이 + 그 차이가 어디서 나는지 세 가지로\n"
    "2. 한 가지만 실천해도 얼마나 오르는지 + 30일 + 전체 상승폭\n"
    "3. 따뜻한 마무리 + {user_name}님 호명\n\n"
    "[출력] 3단락만.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- current_score: {current_score}
- target_score: {target_score}
- gap_per_action: {gap_per_action}
- overall_boost_pct: {overall_boost_pct}

[기반]
{rule_text}

[요청] 3단락 220~340자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "current_score", "target_score",
    "gap_per_action", "overall_boost_pct", "rule_text",
}


def build_p9_optimize_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 400


def validate_p9_optimize(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "current_score", "target_score",
              "gap_per_action", "overall_boost_pct"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
