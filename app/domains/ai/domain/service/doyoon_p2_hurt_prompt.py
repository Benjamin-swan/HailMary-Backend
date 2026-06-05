"""도윤 P-2 1-4 약점 트리거 — AI prompt builder + validate.

원본 도윤 구조 정합 (2026-05-21 재설계).
4단락 250~400자. 두 hurt_type 분석 + 처방.
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
    '- 존댓말 사용, "{user_name}님" 호명 (단락 2 또는 3에서 1회)\n'
    "- 약한 고리 두 가지를 데이터 근거로 짚되, 위험은 단정 대신 '이런 흐름에서 흔들리기 쉬워요'처럼 풀어준다\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 마지막에 다시 일어설 수 있다는 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})\n"
    "- 약점 키워드 1 ({hurt_type_1_keyword}) + 위험도 ({hurt_type_1_risk_pct})\n"
    "- 약점 키워드 2 ({hurt_type_2_keyword}) + 위험도 ({hurt_type_2_risk_pct})\n"
    "- 개입 효과 ({intervention_drop_pct})\n\n"
    "[구성] 4 단락, 단락 사이 빈 줄 1개, 총 230~400자\n"
    "1. 두 유형 도입 (1문장)\n"
    "2. 첫 번째 유형 분석 + 위험도 (2~3문장)\n"
    "3. 두 번째 유형 분석 + 위험도 (1~2문장)\n"
    "4. 처방 + 개입 효과 (2문장)\n\n"
    "[출력] 4단락 텍스트만. 메타·헤더 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-2 약점 트리거 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- hurt_type_1_keyword: {hurt_type_1_keyword}
- hurt_type_1_risk_pct: {hurt_type_1_risk_pct}
- hurt_type_2_keyword: {hurt_type_2_keyword}
- hurt_type_2_risk_pct: {hurt_type_2_risk_pct}
- intervention_drop_pct: {intervention_drop_pct}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 4단락 230~400자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "hurt_type_1_keyword",
    "hurt_type_1_risk_pct",
    "hurt_type_2_keyword",
    "hurt_type_2_risk_pct",
    "intervention_drop_pct",
    "rule_text",
}


def build_p2_hurt_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ilgan_hanja=facts["ilgan_hanja"],
        hurt_type_1_keyword=facts["hurt_type_1_keyword"],
        hurt_type_1_risk_pct=facts["hurt_type_1_risk_pct"],
        hurt_type_2_keyword=facts["hurt_type_2_keyword"],
        hurt_type_2_risk_pct=facts["hurt_type_2_risk_pct"],
        intervention_drop_pct=facts["intervention_drop_pct"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 500


def validate_p2_hurt(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["ilgan_hanja"] not in text:
        return False, f"ilgan_hanja missing: {facts['ilgan_hanja']!r}"
    if facts["hurt_type_1_keyword"] not in text:
        return False, f"hurt_type_1_keyword missing: {facts['hurt_type_1_keyword']!r}"
    if facts["hurt_type_1_risk_pct"] not in text:
        return False, f"hurt_type_1_risk_pct missing: {facts['hurt_type_1_risk_pct']!r}"
    if facts["hurt_type_2_keyword"] not in text:
        return False, f"hurt_type_2_keyword missing: {facts['hurt_type_2_keyword']!r}"
    if facts["hurt_type_2_risk_pct"] not in text:
        return False, f"hurt_type_2_risk_pct missing: {facts['hurt_type_2_risk_pct']!r}"
    if facts["intervention_drop_pct"] not in text:
        return False, f"intervention_drop_pct missing: {facts['intervention_drop_pct']!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2 or 3)"
    return True, ""
