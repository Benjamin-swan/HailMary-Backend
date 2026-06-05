"""도윤 P-4 2-4 착각 인연 — AI prompt builder + validate."""

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
    '- 존댓말, "{user_name}님" 호명 (마지막 단락 1회)\n'
    "- 진짜 인연처럼 보이지만 착각하기 쉬운 관계를, 시간에 따른 변화로 짚어준다\n"
    "- 헷갈리게 만드는 신호를 차분히 풀어주되, 단정 대신 흐름으로 설명한다\n"
    "- 따뜻함은 절제하되, 마지막에 사람을 향한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n\n"
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 ({ilgan_full})\n"
    "- 헷갈리기 쉬운 신호 키워드 3종 ({sign_1_keyword} / {sign_2_keyword} / {sign_3_keyword})\n"
    "- 신호 발생률 3종 ({sign_1_pct} / {sign_2_pct} / {sign_3_pct})\n"
    "- 진짜 인연 성장률 ({real_growth_pct}) + 착각 인연 하락률 ({fake_drop_pct})\n\n"
    "[구성] 4 단락, 총 290~500자\n"
    "1. 일간별 착각 발생률 (1~2문장)\n"
    "2. 3개월쯤 지나면 진짜와 착각이 갈리는 변화 (2~3문장)\n"
    "3. 헷갈리기 쉬운 신호 3종 요약 (2~3문장)\n"
    "4. {user_name}님 호명 + 마지막 한 줄\n\n"
    "[출력] 4단락 텍스트만. 메타·헤더 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-4 착각 인연 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- sign_1_keyword: {sign_1_keyword}
- sign_1_pct: {sign_1_pct}
- sign_2_keyword: {sign_2_keyword}
- sign_2_pct: {sign_2_pct}
- sign_3_keyword: {sign_3_keyword}
- sign_3_pct: {sign_3_pct}
- real_growth_pct: {real_growth_pct}
- fake_drop_pct: {fake_drop_pct}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 4단락 290~500자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "illusion_multiplier",
    "sign_1_keyword",
    "sign_1_pct",
    "sign_2_keyword",
    "sign_2_pct",
    "sign_3_keyword",
    "sign_3_pct",
    "real_growth_pct",
    "fake_drop_pct",
    "accuracy_multiplier",
    "rule_text",
}


def build_p4_illusion_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 260
_MAX_LENGTH = 600


def validate_p4_illusion(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, "ilgan_full missing"
    for k in ("real_growth_pct", "fake_drop_pct",
              "sign_1_keyword", "sign_1_pct",
              "sign_2_keyword", "sign_2_pct",
              "sign_3_keyword", "sign_3_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2 or 3)"
    return True, ""
