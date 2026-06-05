"""도윤 P-4 2-3 비호환 — AI prompt builder + validate."""

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
    '- 존댓말, "{user_name}님" 호명 (마지막 단락에서 1회)\n'
    "- 두 사람이 잘 맞지 않는 결을 외형·첫인상·시간에 따른 변화로 차분히 짚어준다\n"
    "- 데이터는 근거로만 쓰고, 잘 맞지 않는 지점도 단정 대신 흐름으로 설명한다\n"
    "- 따뜻함은 절제하되, 마지막에 사람을 향한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n\n"
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 ({ilgan_full})\n"
    "- 키 분포 ({height_distribution_pct})\n"
    "- 첫인상 / 6개월 / 격차 ({impression_first} / {impression_6m} / {impression_gap})\n"
    "- 비슷한 사례 비율 ({common_signal_pct})\n\n"
    "[구성] 4 단락, 단락 사이 빈 줄 1개, 총 320~520자\n"
    "1. 데이터 정리 완료 신호 (1문장)\n"
    "2. 외형 데이터 — 키 분포, 체형, 얼굴상, 이목구비 (2~3문장)\n"
    "3. 첫인상과 6개월 뒤 인상의 격차 풀이 (2~3문장)\n"
    "4. {ilgan_full} 일간과의 결이 시간이 지날수록 어긋나는 흐름 + 거리 두기 권유 "
    "+ {user_name}님 호명 (3문장)\n\n"
    "[출력] 4단락 텍스트만. 메타·헤더 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-4 비호환 프로파일 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- height_distribution_pct: {height_distribution_pct}
- impression_first: {impression_first}
- impression_6m: {impression_6m}
- impression_gap: {impression_gap}
- common_signal_pct: {common_signal_pct}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 4단락 320~520자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "height_distribution_pct",
    "impression_first",
    "impression_6m",
    "impression_gap",
    "emotional_volatility_multiplier",
    "common_signal_pct",
    "rule_text",
}


def build_p4_akyon_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in (
        "user_name", "ilgan_full", "height_distribution_pct",
        "impression_first", "impression_6m", "impression_gap", "common_signal_pct",
    )})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in (
        "user_name", "ilgan_full", "height_distribution_pct",
        "impression_first", "impression_6m", "impression_gap",
        "common_signal_pct", "rule_text",
    )})
    return system, user


_MIN_LENGTH = 290
_MAX_LENGTH = 600


def validate_p4_akyon(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, "ilgan_full missing"
    for k in ("height_distribution_pct", "impression_first", "impression_6m",
              "impression_gap", "common_signal_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 3:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 3)"
    return True, ""
