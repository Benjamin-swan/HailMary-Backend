"""도윤 P-3 2-2 반복 패턴 — AI prompt builder + validate."""

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
    '- 존댓말 사용, "{user_name}님" 호명 (단락 1에서 1회)\n'
    "- 관계에서 반복되는 행동의 흐름을 단계별로 차분히 짚어준다 — 같은 장면이 어떻게 되풀이되는지\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 흐름을 바꿀 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 ({ilgan_full})\n"
    "- 패턴 키워드 3종 ({pattern_1_keyword} / {pattern_2_keyword} / {pattern_3_keyword})\n"
    "- 패턴 발생률 3종 ({pattern_1_pct} / {pattern_2_pct} / {pattern_3_pct})\n"
    "- 안정성 부스트 ({stability_boost_pct})\n"
    "위 값들은 변경·누락·풀어쓰기·약어화 모두 금지. 출력에 그대로 포함돼야 합니다.\n\n"
    "[구성] 4 단락, 총 230~400자\n"
    "1. 도입 (1문장)\n"
    "2. 첫 번째 반복 패턴 풀이\n"
    "3. 두 번째 + 세 번째 반복 패턴 풀이\n"
    "4. {ilgan_full} 일간 특유의 흐름 + 안정성 부스트\n\n"
    "[출력] 4단락 텍스트만. 메타·헤더 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-3 반복 실수 패턴 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- pattern_1_keyword: {pattern_1_keyword}
- pattern_1_pct: {pattern_1_pct}
- pattern_2_keyword: {pattern_2_keyword}
- pattern_2_pct: {pattern_2_pct}
- pattern_3_keyword: {pattern_3_keyword}
- pattern_3_pct: {pattern_3_pct}
- stability_boost_pct: {stability_boost_pct}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 4단락 230~400자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "pattern_1_keyword",
    "pattern_1_pct",
    "pattern_2_keyword",
    "pattern_2_pct",
    "pattern_3_keyword",
    "pattern_3_pct",
    "stability_boost_pct",
    "rule_text",
}


def build_p3_pattern_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 500


def validate_p3_pattern(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    for k in ("pattern_1_keyword", "pattern_2_keyword", "pattern_3_keyword",
              "pattern_1_pct", "pattern_2_pct", "pattern_3_pct",
              "stability_boost_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2 or 3)"
    return True, ""
