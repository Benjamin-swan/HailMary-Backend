"""도윤 P-5 3-2 전환율 — AI prompt + validate."""

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
    '- 존댓말 사용, "{user_name}님" 호명 (단락 2 또는 3에서)\n'
    "- 첫 만남부터 끌림까지 마음이 움직이는 단계를 차분히 따라가며 설명한다\n"
    "- 두 번째 만남에서 분위기가 달라지는 지점을 짚고, 마지막에 실천할 한 줄을 건넨다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "다음 값은 *변경, 누락, 풀어쓰기, 약어화* 모두 금지하고 그대로 출력에 포함:\n"
    "- {user_name}, {ilgan_full}\n"
    "- 4단계 % ({step_1_pct} → {step_2_pct} → {step_3_pct} → {step_4_pct})\n"
    "- 두 번째 만남 배수 ({second_meeting_multiplier})\n"
    "- 호감도 차이 ({final_gap_pct})\n\n"
    "[구성] 3 단락, 총 180~330자\n"
    "1. 4단계 흐름 도입\n"
    "2. 두 번째 만남에서 달라지는 점 + 차이\n"
    "3. 실천할 한 줄 + {user_name}님 호명\n\n"
    "[출력] 3단락만 출력. 메타 설명·주석·헤더·코드블록 금지.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- step_1_pct: {step_1_pct}
- step_2_pct: {step_2_pct}
- step_3_pct: {step_3_pct}
- step_4_pct: {step_4_pct}
- second_meeting_multiplier: {second_meeting_multiplier}
- final_gap_pct: {final_gap_pct}

[기반]
{rule_text}

[요청] 3단락 180~330자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "step_1_pct", "step_2_pct", "step_3_pct", "step_4_pct",
    "second_meeting_multiplier", "final_gap_pct", "rule_text",
}


def build_p5_conversion_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 160
_MAX_LENGTH = 400


def validate_p5_conversion(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    # 4단계 % 중 최소 3개 포함
    pcts_found = sum(1 for k in ("step_1_pct", "step_2_pct", "step_3_pct", "step_4_pct") if facts[k] in text)
    if pcts_found < 3:
        return False, f"conversion steps insufficient: {pcts_found}/4"
    if facts["second_meeting_multiplier"] not in text:
        return False, "second_meeting_multiplier missing"
    if facts["final_gap_pct"] not in text:
        return False, "final_gap_pct missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
