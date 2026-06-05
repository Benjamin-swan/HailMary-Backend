"""도윤 P-10 box1 — 사용자 입력 상황 분석 AI prompt + validate.

동적 글자수: 선택 옵션 수에 비례 (1개 → ~400자, 4개 → ~800자).
페이지 라벨(예: "X장", "다음 장") 언급 금지 — 데이터 직접 인용.
"""

from __future__ import annotations

from app.domains.ai.domain.service.doyoon_tone_guide import (
    DOYOON_FORBIDDEN_BLOCK,
    DOYOON_TONE_GUIDE,
)
from app.domains.ai.domain.templates.doyoon_p10_box_letter import (
    calc_box_length_range,
)

_BASE_MIN = 350
_BASE_MAX = 480


# 공유 톤 블록은 placeholder({})가 없어 .format() 안전 — 문자열 결합으로 삽입.
_SYSTEM_PROMPT_TPL = (
    "당신은 도화선 캐릭터 한도윤 — 사주 데이터를 사람 말로 풀어주는 상담형 분석가.\n\n"
    + DOYOON_TONE_GUIDE + "\n\n"
    "[페르소나]\n"
    '- 존댓말, "{user_name}님" 호명 (단락마다 강박적 반복은 피하고 자연스럽게)\n'
    "- 데이터는 근거로만 깔고, 설명은 상담하듯 일상어로 — 감정 흐름·반복 패턴·관계에서 속도가 붙는 지점을 짚는다\n"
    "- 분석적이되 끝에 사람을 향한 따뜻한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "네가" 반말 금지 — 존댓말 일관\n\n'
    "[페이지 언급 금지]\n"
    '- "X장에서", "다음 장에서", "뒤에", "앞으로 풀어드릴게요" 같은 외부 참조 절대 금지\n'
    "- answer_data에 박힌 사실값을 *지금 이 박스 안에서 직접* 풀어줄 것\n\n"
    "[사실값 보존 — 변형 금지]\n"
    "- 사용자 이름: {user_name}\n"
    "- 일간: {ilgan_full}({ilgan_hanja})\n"
    "- 선택 상황 라벨: {step1_labels}\n"
    "- 옵션별 답 데이터: answer_data 블록에 정리됨 (수치·키워드 그대로 인용)\n\n"
    "[구성] {step1_count}개 옵션 → {min_len}~{max_len}자, 단락 {min_para}~{max_para}개\n"
    "1. 도입 — {user_name}님 호명 + 입력 정리\n"
    "2. 일간 풀이 — 어떤 결의 흐름인지 일상어로\n"
    "3+. 옵션별 답 데이터 자연 인용 (선택 옵션 수에 따라 분량 조절)\n"
    "N. 권장 행동 + {user_name}님 호명 클로징\n\n"
    "[출력] 본문 텍스트만. 메타·헤더 금지.\n"
)


_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- step1_count: {step1_count}
- step1_labels: {step1_labels}

[answer_data — 옵션별 답 사실값 (페이지 언급 X, 그대로 인용)]
{answer_data}

[룰 기반 텍스트 — 표현 다양화 OK, 사실값/수치/키워드는 그대로]
{rule_text}

[요청] {min_len}~{max_len}자, {min_para}~{max_para}단락.
"""


_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "step1_labels", "step1_count", "answer_data", "rule_text",
}


def _para_range(option_count: int) -> tuple[int, int]:
    """옵션 수별 단락 수."""
    return (3, 4) if option_count <= 2 else (4, 5)


def build_p10_box1_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    option_count = int(facts.get("step1_count", "1"))
    min_len, max_len = calc_box_length_range(option_count, base_min=_BASE_MIN, base_max=_BASE_MAX)
    min_para, max_para = _para_range(option_count)

    fmt_keys = {
        **{k: facts[k] for k in _REQUIRED_KEYS},
        "min_len": str(min_len),
        "max_len": str(max_len),
        "min_para": str(min_para),
        "max_para": str(max_para),
    }
    system = _SYSTEM_PROMPT_TPL.format(**fmt_keys)
    user = _USER_PROMPT_TPL.format(**fmt_keys)
    return system, user


def validate_p10_box1(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    option_count = int(facts.get("step1_count", "1"))
    min_len, max_len = calc_box_length_range(option_count, base_min=_BASE_MIN, base_max=_BASE_MAX)
    # 검증은 +-20% 여유
    soft_min = int(min_len * 0.85)
    soft_max = int(max_len * 1.15)

    length = len(text)
    if length < soft_min or length > soft_max:
        return False, f"length out of range: {length} (expected {soft_min}~{soft_max} for {option_count} options)"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, "ilgan_full missing"

    # 페이지 언급 금지 — 발견 시 fail
    forbidden_page_terms = ["다음 장", "뒤 장", "앞 장", "장에서 풀", "장에서 알려", "다음 페이지"]
    for term in forbidden_page_terms:
        if term in text:
            return False, f"forbidden page reference: {term!r}"

    min_para, _ = _para_range(option_count)
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks < min_para - 1:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected >= {min_para - 1})"
    return True, ""
