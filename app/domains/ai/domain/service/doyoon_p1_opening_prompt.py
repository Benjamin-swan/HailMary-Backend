"""도윤 P-1 1-1 Ch1 오프닝 — AI prompt builder + validate.

호출자: generate_p1_opening_usecase. 입력 facts는 doyoon_p1_opening.get_doyoon_p1_opening_facts.

전략: 룰 합성 결과를 *기반 텍스트*로 AI에 전달 → 같은 사실값 보존하면서 표현 다양화.
P-0 doyoon_p0_diagnosis_prompt.py 패턴과 동일.

순수 도메인 — 외부 라이브러리 import 금지 (CLAUDE.md Domain 규칙).
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
    '- 존댓말, "{user_name}님" 호명 (단락 1에서 1회)\n'
    "- 데이터는 근거로만 쓰고, 설명은 일상어로 — 어려운 개념은 먼저 쉬운 말로 풀어준다\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 분석 끝에 사람을 향한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})\n"
    "- 일주 한자 ({ilju_hanja})\n"
    "- 상위 N% ({pct_value}), 분포 N% ({distribution_pct})\n"
    "- 연애 유형 ({love_type})\n"
    "출력 텍스트에 위 문자열들이 그대로 포함돼야 합니다.\n\n"
    "[구성] 4 단락, 단락 사이 빈 줄 1개, 총 320~440자\n"
    "1. 호명 + 상위 N% 자리에 든다는 신호 (1~2문장)\n"
    "2. 분포 N% + 연애 유형 + 일주를 묶어 어떤 결인지 (2문장)\n"
    "3. 일간 진단 — 관계에서 드러나는 성향을 일상어로 (2문장)\n"
    "4. 도움이 될 작은 행동 하나 (1~2문장)\n\n"
    "[출력]\n"
    "4단락 텍스트만. 메타 설명·헤더·코드블록 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-1 Ch1 오프닝을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- ilju_hanja: {ilju_hanja}
- pct_value: {pct_value}
- distribution_pct: {distribution_pct}
- love_type: {love_type}

[참고 — 일간 진단 본문]
{ilgan_diagnosis_text}

[참고 — 최적화 가이드 본문 ({user_name} 박힘)]
{ilgan_optimization_text}

[룰 합성 기반 텍스트 — 이걸 *기반으로* 같은 사실값을 모두 보존한 채 표현을 다양화하세요. \
그대로 복붙 금지 (연결사·문장 길이·구성 다양화). 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값을 모두 포함하는 4단락 320~440자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "ilju_hanja",
    "pct_value",
    "distribution_pct",
    "love_type",
    "ilgan_diagnosis_text",
    "ilgan_optimization_text",
    "rule_text",
}


def build_p1_opening_prompt(facts: dict[str, str]) -> tuple[str, str]:
    """facts dict → (system_prompt, user_prompt). 필수 키 누락 시 KeyError."""
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")

    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ilgan_hanja=facts["ilgan_hanja"],
        ilju_hanja=facts["ilju_hanja"],
        pct_value=facts["pct_value"],
        distribution_pct=facts["distribution_pct"],
        love_type=facts["love_type"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


# ── 출력 검증 ─────────────────────────────────────────────────────


_MIN_LENGTH = 280
_MAX_LENGTH = 550


def validate_p1_opening(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    """AI 출력 검증. 실패 시 (False, 사유)."""
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"

    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["ilgan_hanja"] not in text:
        return False, f"ilgan_hanja missing: {facts['ilgan_hanja']!r}"
    if facts["ilju_hanja"] not in text:
        return False, f"ilju_hanja missing: {facts['ilju_hanja']!r}"
    if facts["pct_value"] not in text:
        return False, f"pct_value missing: {facts['pct_value']!r}"
    if facts["distribution_pct"] not in text:
        return False, f"distribution_pct missing: {facts['distribution_pct']!r}"
    if facts["love_type"] not in text:
        return False, f"love_type missing: {facts['love_type']!r}"

    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 3:
        return False, f"paragraph structure invalid: {paragraph_breaks} breaks (expected 3)"

    return True, ""
