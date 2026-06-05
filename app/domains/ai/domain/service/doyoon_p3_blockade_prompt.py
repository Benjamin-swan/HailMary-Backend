"""도윤 P-3 2-1 구조적 원인 — AI prompt builder + validate."""

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
    "- 오행이 한쪽으로 쏠리며 관계가 막히는 흐름을, 숫자가 아니라 일상의 장면으로 풀어준다\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 비우면 달라지는 방향을 차분히 짚어준다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 ({ilgan_full})\n"
    "- 오행 과다 ({ohang_excess}) + 한자 ({ohang_excess_hanja})\n"
    "- 기운 강도 표현 ({blockade_multiplier})\n"
    "위 값들은 변경·누락·풀어쓰기·약어화 모두 금지. 출력에 그대로 포함돼야 합니다.\n\n"
    "[수치 금지] 이 화면엔 그래프·수치 그래픽이 없어, 퍼센트(%)를 쓰면 근거 없는 숫자로 보여 반발을 부릅니다. "
    "%·배수 등 숫자는 본문에 절대 쓰지 말고 '눈에 띄게 더디게', '한결 가벼워진다'처럼 말로 풀어주세요.\n\n"
    "[구성] 3 단락, 단락 사이 빈 줄 1개, 총 270~430자\n"
    "1. 호명 + 오행이 어느 쪽으로 쏠려 있는지 (1~2문장)\n"
    "2. 그 쏠림이 관계를 막는 양상 (2~3문장)\n"
    "3. 비우면 달라지는 방향 + 한 줄 제안 (2~3문장)\n\n"
    "[출력] 3단락 텍스트만. 메타·헤더 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-3 구조적 원인 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ohang_excess: {ohang_excess}
- ohang_excess_hanja: {ohang_excess_hanja}
- blockade_multiplier: {blockade_multiplier}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 3단락 270~430자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "ohang_excess",
    "ohang_excess_hanja",
    "blockade_pct",
    "blockade_multiplier",
    "rule_text",
}


def build_p3_blockade_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ohang_excess=facts["ohang_excess"],
        ohang_excess_hanja=facts["ohang_excess_hanja"],
        blockade_multiplier=facts["blockade_multiplier"],
    )
    user = _USER_PROMPT_TPL.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ohang_excess=facts["ohang_excess"],
        ohang_excess_hanja=facts["ohang_excess_hanja"],
        blockade_multiplier=facts["blockade_multiplier"],
        rule_text=facts["rule_text"],
    )
    return system, user


_MIN_LENGTH = 240
_MAX_LENGTH = 500


def validate_p3_blockade(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ohang_excess_hanja"] not in text:
        return False, f"ohang_excess_hanja missing: {facts['ohang_excess_hanja']!r}"
    # blockade_multiplier(비수치 강도 표현)는 배수 게이트 완화로 필수 포함 검사에서 제외.
    # blockage_rate_drop / recovery_after_clearing_pct(%) 2026-06-05 폐기 — 그래프 없는 화면에 수치 노출 금지.
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2)"
    return True, ""
