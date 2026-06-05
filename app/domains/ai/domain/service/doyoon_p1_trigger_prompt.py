"""도윤 P-1 1-2 트리거 메커니즘 — AI prompt builder + validate.

2단락 200~280자. P-0/P-1 opening 패턴 동일.
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
    '- 존댓말, "{user_name}님" 호명 (단락 2에서 1회)\n'
    "- 마음이 흔들리는 순간과 반복되는 행동 패턴을 차분히 짚어준다\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 분석 끝에 사람을 향한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 ({ilgan_full})\n"
    "- 도달 수치 ({trigger_completion_pct})\n"
    "- 초기 진입 시간 ({peak_window_days})\n"
    "- 마음을 다잡기 어려운 정도 ({self_control_pct})\n"
    "출력 텍스트에 위 문자열들이 그대로 포함돼야 합니다.\n\n"
    "[구성] 2 단락, 단락 사이 빈 줄 1개, 총 180~310자\n"
    "1. 마음을 흔드는 신호 3가지가 차례로 겹칠 때 {trigger_completion_pct}가 의미하는 바 (1~2문장)\n"
    "2. {peak_window_days} 초기 + 첫 두 신호가 겹칠 때 + 마음을 다잡기 어려운 정도 {self_control_pct} (3~4문장)\n\n"
    "[출력] 2단락 텍스트만. 메타 설명·헤더·코드블록 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-1 트리거 메커니즘 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- trigger_1: {trigger_1}
- trigger_2: {trigger_2}
- trigger_completion_pct: {trigger_completion_pct}
- peak_window_days: {peak_window_days}
- self_control_pct: {self_control_pct}

[참고 — 자기조절 어려운 이유 본문]
{control_reason_text}

[룰 합성 기반 텍스트 — 이걸 *기반으로* 같은 사실값을 모두 보존한 채 표현을 다양화하세요. \
그대로 복붙 금지. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값을 모두 포함하는 2단락 180~310자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "trigger_1",
    "trigger_2",
    "trigger_3",
    "trigger_completion_pct",
    "peak_window_days",
    "self_control_pct",
    "control_reason_text",
    "rule_text",
}


def build_p1_trigger_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")

    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        trigger_completion_pct=facts["trigger_completion_pct"],
        peak_window_days=facts["peak_window_days"],
        self_control_pct=facts["self_control_pct"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 160
_MAX_LENGTH = 380


def validate_p1_trigger(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"

    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["trigger_completion_pct"] not in text:
        return False, "trigger_completion_pct missing"
    if facts["peak_window_days"] not in text:
        return False, "peak_window_days missing"
    if facts["self_control_pct"] not in text:
        return False, "self_control_pct missing"
    # trigger_1, trigger_2 중 적어도 둘은 포함 (룰 본문에 둘 다 박혀있음)
    if facts["trigger_1"] not in text:
        return False, "trigger_1 missing"
    if facts["trigger_2"] not in text:
        return False, "trigger_2 missing"

    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 1:
        return False, f"paragraph structure invalid: {paragraph_breaks} breaks (expected 1)"

    return True, ""
