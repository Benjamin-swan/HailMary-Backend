"""도윤 P-2 1-5 회복 곡선 — AI prompt builder + validate.

원본 도윤 구조 정합 (2026-05-21 재설계). 진행바 4단계 % + 평균 회복 곡선 분석.
3~4 단락 280~500자.
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
    '- 존댓말 사용, "{user_name}님" 호명 (단락 2 이후 1회)\n'
    "- 회복이 어떻게 풀려가는지를 시간 순서대로 차분히 짚어주되, 숫자는 '이쯤이면 한결 가벼워져요'처럼 일상어로 받쳐준다\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 끝에 다시 회복된다는 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})\n"
    "- 평균 대비 회복 지연 ({recovery_lag_multiplier})\n\n"
    "[구성] 3~4 단락, 총 260~500자\n"
    "1. 도입 — 평균적인 회복 흐름 소개 (1~2문장)\n"
    "2. 시간 흐름 — 직후/한 달/세 달/여섯 달로 가벼워지는 과정 (2~3문장)\n"
    "   ※ 회복률 퍼센트는 이미 위 진행바에 있습니다. 여기선 수치를 쓰지 말고 문장으로만 풀어주세요.\n"
    "3. 평균 대비 지연 평가 + 처방 (2~3문장)\n\n"
    "[출력] 텍스트만. 메타·헤더 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-2 회복 곡선 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- recovery_lag_multiplier: {recovery_lag_multiplier}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 3~4단락 260~500자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "recovery_lag_multiplier",
    "rule_text",
}


def build_p2_recovery_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ilgan_hanja=facts["ilgan_hanja"],
        recovery_lag_multiplier=facts["recovery_lag_multiplier"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 230
_MAX_LENGTH = 600


def validate_p2_recovery(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["ilgan_hanja"] not in text:
        return False, f"ilgan_hanja missing: {facts['ilgan_hanja']!r}"
    # recovery_lag_multiplier(비수치)·회복률 수치는 출력 필수 포함 검사 제거.
    # 단락2 회복률 %는 진행바와 중복돼 폐기(2026-06-05) — 본문 검증 대상 아님.
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2 or 3)"
    return True, ""
