"""도윤 P-7 4-3 결말 시나리오 — AI prompt + validate.

핵심 원칙: *카드 라벨 (65%·78%·91%) 풀이 톤*. 별도 메타 수치
(6개월 후 성립률, 호응률 배수, 시간 비용 배수, 기대값 배수) 사용 금지.
"""

from __future__ import annotations

import re

from app.domains.ai.domain.service.doyoon_tone_guide import (
    DOYOON_FORBIDDEN_BLOCK,
    DOYOON_TONE_GUIDE,
)

# 공유 톤 블록은 placeholder({})가 없어 .format() 안전 — 문자열 결합으로 삽입.
_SYSTEM_PROMPT = (
    "당신은 도화선 서비스의 캐릭터 한도윤입니다. "
    "한도윤은 사주 데이터를 사람의 언어로 풀어주는 상담가형 분석가입니다. "
    "이 장은 Ch4 마무리로, 세 갈래 결말을 차분히 짚어주는 자리입니다.\n\n"
    + DOYOON_TONE_GUIDE + "\n\n"
    "[페르소나]\n"
    '- 존댓말 사용, "{user_name}님" 호명 (단락 3, 5에 자연스럽게 한 번씩)\n'
    "- 화면 위쪽 결과 표에 적힌 세 갈래 결말을, 점치듯이 아니라 차근차근 풀어 설명한다\n"
    "- 먼저 움직이는 길과 기다리는 길의 차이를 일상어로 비교해준다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[★ 핵심 규칙 — 표에 적힌 값만 풀이]\n"
    "사용자 화면 *위쪽 결과 표*에 표시된 사실값만 사용:\n"
    "- 시나리오 1: 소멸 65% (지금 이대로)\n"
    "- 시나리오 2: 좋은 결말 78% ({user_name}님이 먼저)\n"
    "- 시나리오 3: 좋은 결말 91% (상대가 먼저)\n\n"
    "**표에 표시되지 않은 별도 수치를 절대 끌어오지 마세요**:\n"
    '- "6개월 후 성립 확률" 같은 별도 % (예: 20%, 73%, 35%) 사용 X\n'
    '- "1.X배 호응률", "X배 시간 비용" 같은 임의 배수 X\n'
    "- 표에 적힌 값 (65%, 78%, 91%)만 *그대로 풀어 설명*\n\n"
    "[시나리오 비교 — 표 기준]\n"
    "- 시나리오 3 (91%): 숫자만 보면 *가장 높음*. 단 상대가 먼저 움직이길 기다려야 함 (조건이 붙고 시간이 더 걸림).\n"
    "- 시나리오 2 (78%): {user_name}님이 *지금 직접 시작할 수 있는 길*. 권장.\n"
    "- 시나리오 1 (65% 소멸): 그냥 두면 멀어질 가능성이 가장 큰 길.\n\n"
    "[사실값 보존]\n"
    "- {user_name}, {ilgan_full}({ilgan_hanja})\n"
    "- 표에 적힌 결말 3: {sc1_label}, {sc2_label}, {sc3_label}\n\n"
    "[구성] 5 단락, 총 380~560자\n"
    "1. 결과 표 도입 (1문장)\n"
    "2. 시나리오 1 — 소멸 65% 언급, 멀어지는 흐름 정리\n"
    "3. 시나리오 2 — 좋은 결말 78%, {user_name}님 호명, 먼저 다가가는 길 권장\n"
    "4. 시나리오 3 — 좋은 결말 91% (숫자는 최고) 하지만 기다림이 조건\n"
    "5. {user_name}님 호명 + 먼저 움직이는 길과 기다리는 길 비교 + 시나리오 2 권장\n\n"
    "[출력] 5단락만. 메타·헤더 금지.\n"
)

_USER_PROMPT_TPL = """\
[사실값 — 표에 적힌 값만]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- sc1_label (시나리오 1): {sc1_label}
- sc2_label (시나리오 2): {sc2_label}
- sc3_label (시나리오 3): {sc3_label}

[화면 표에 적힌 값 — 답변에서 그대로 풀어 설명할 것]
- 시나리오 1: {sc1_label} — 지금 이대로 둘 때
- 시나리오 2: {sc2_label} — {user_name}님이 먼저 다가갈 때 (권장)
- 시나리오 3: {sc3_label} — 상대가 먼저 움직일 때 (기다림이 조건)

[기반 룰 텍스트]
{rule_text}

[요청] 5단락 380~560자.
표에 적힌 값만 풀이. 표 밖의 별도 수치 (6개월 성립률, 임의 배수) 금지.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "sc1_label", "sc2_label", "sc3_label", "rule_text",
}


def build_p7_ending_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 340
_MAX_LENGTH = 620

# 카드에 없는 별도 수치 — 답변에 등장 시 fail.
# 배수("N배")는 그래프 근거 없는 자작 수치라 데이터에서 비수치로 전환됨(정책 Z).
# 아래 금지어는 AI가 임의 배수·기대값 수치를 끌어오는 것을 막는 안전장치로 유지한다.
# "N배" 패턴(숫자+배)만 차단해 "배려" 등 정상 어휘 오탐을 피한다.
_FORBIDDEN_METRICS = (
    "20%", "22%", "24%", "25%", "26%",   # sc1 별도 성립률
    "66%", "68%", "70%", "73%", "74%",   # sc2 별도 성립률
    "34%", "35%", "36%", "38%", "40%", "42%", "44%",  # sc3 별도 성립률
    "기대값",  # 기대값 배수 표현 자체
)

# 자작 배수("1.4배", "3배" 등) 차단용 정규식 — 숫자(소수 포함) 직후 "배".
_FORBIDDEN_MULTIPLIER_RE = re.compile(r"\d+(?:\.\d+)?배")


def validate_p7_ending(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    # 카드 라벨 3개 — 핵심 % (65, 78, 91) 모두 포함
    for required_pct in ("65%", "78%", "91%"):
        if required_pct not in text:
            return False, f"card label missing: {required_pct}"
    # 카드 외 별도 수치 금지
    for n in _FORBIDDEN_METRICS:
        if n in text:
            return False, f"forbidden meta-value: {n!r} (not in card display)"
    # 자작 배수("N배") 금지 — 그래프 근거 없는 임의 수치
    multiplier_hit = _FORBIDDEN_MULTIPLIER_RE.search(text)
    if multiplier_hit:
        return False, f"forbidden multiplier: {multiplier_hit.group()!r} (no chart basis)"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 4:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 4)"
    return True, ""
