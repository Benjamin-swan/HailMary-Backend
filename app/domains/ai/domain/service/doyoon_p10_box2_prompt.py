"""도윤 P-10 box2 — 사용자 알고싶은 영역 분석 AI prompt + validate.

동적 글자수: 선택 옵션 수에 비례 (1개 → ~450자, 4개 → ~900자).
페이지 라벨 언급 금지 — answer_data에 박힌 수치/keyword 직접 인용.
"""

from __future__ import annotations

from app.domains.ai.domain.service.doyoon_tone_guide import (
    DOYOON_FORBIDDEN_BLOCK,
    DOYOON_TONE_GUIDE,
)
from app.domains.ai.domain.templates.doyoon_p10_box_letter import (
    calc_box_length_range,
)

_BASE_MIN = 400
_BASE_MAX = 550


# 공유 톤 블록은 placeholder({})가 없어 .format() 안전 — 문자열 결합으로 삽입.
_SYSTEM_PROMPT_TPL = (
    "당신은 도화선 캐릭터 한도윤 — 사주 데이터를 사람 말로 풀어주는 상담형 분석가.\n\n"
    + DOYOON_TONE_GUIDE + "\n\n"
    "[페르소나]\n"
    '- 존댓말, "{user_name}님" 호명 (단락마다 반복하지 말고 자연스럽게)\n'
    "- 답할 수 있는 질문과 그렇지 않은 질문을 차분히 나눠 보여주고, 답 가능한 부분은 일상어로 풀어준다\n"
    "- 분석적이되 답을 *지금 박스 안에서* 직접 풀어줄 것\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "네가" 반말 금지\n\n'
    "[페이지 언급 절대 금지]\n"
    '- "X장에서", "다음 장에서", "뒤에서 풀어드려요", "다음 페이지에서" 등 외부 참조 금지\n'
    "- answer_data 블록에 박힌 사실값을 *지금 이 박스 안에서 직접 풀어줄 것*\n"
    '- "다음에 알려드려요" 식의 약속도 금지\n\n'
    "[사실값 보존]\n"
    "- 사용자 이름: {user_name}\n"
    "- 일간: {ilgan_full}({ilgan_hanja})\n"
    "- 질문 영역 라벨: {step2_labels}\n"
    "- 오행 보완: {ohang_lack}({ohang_lack_hanja})\n"
    "- answer_data: 옵션별 답 데이터 (키워드·시기 살리되 퍼센트·점수는 풀어서)\n\n"
    "[수치 표현 규칙]\n"
    "- 퍼센트(%)·점수(점) 같은 숫자는 화면에 그대로 쓰지 말고 '~할 가능성이 높네요', "
    "'자주 보이는 편이에요'처럼 정도로 풀어주세요. %로 쓰면 딱딱하게 느껴집니다.\n"
    "- 단, '다음 인연 시기'의 몇 월(月)은 데이터라 그대로 인용하세요.\n\n"
    "[구성] {step2_count}개 옵션 → {min_len}~{max_len}자, 단락 {min_para}~{max_para}개\n"
    "1. 도입 — {user_name}님 호명 + 질문 영역 정리\n"
    "2+. 옵션별 답 데이터 *지금 박스 안에서* 직접 풀이 (선택한 옵션 수에 비례)\n"
    "N. 알 수 있는 것과 아직 알기 어려운 것 정리 + {user_name}님 클로징\n\n"
    "[출력] 본문 텍스트만.\n"
)


_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- step2_count: {step2_count}
- step2_labels: {step2_labels}
- ohang_lack: {ohang_lack}
- ohang_lack_hanja: {ohang_lack_hanja}

[answer_data — 옵션별 답 사실값 (페이지 언급 X, 지금 박스 안에서 직접 풀이)]
{answer_data}

[룰 기반 텍스트]
{rule_text}

[요청] {min_len}~{max_len}자, {min_para}~{max_para}단락.
"""


_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "step2_labels", "step2_count",
    "ohang_lack", "ohang_lack_hanja", "answer_data", "rule_text",
}


def _para_range(option_count: int) -> tuple[int, int]:
    return (3, 4) if option_count <= 2 else (4, 5)


def build_p10_box2_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    option_count = int(facts.get("step2_count", "1"))
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


def validate_p10_box2(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    option_count = int(facts.get("step2_count", "1"))
    min_len, max_len = calc_box_length_range(option_count, base_min=_BASE_MIN, base_max=_BASE_MAX)
    soft_min = int(min_len * 0.85)
    soft_max = int(max_len * 1.15)

    length = len(text)
    if length < soft_min or length > soft_max:
        return False, f"length out of range: {length} (expected {soft_min}~{soft_max} for {option_count} options)"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, "ilgan_full missing"

    forbidden_page_terms = ["다음 장", "뒤 장", "앞 장", "장에서 풀", "장에서 알려", "다음 페이지", "뒤에서 풀"]
    for term in forbidden_page_terms:
        if term in text:
            return False, f"forbidden page reference: {term!r}"

    min_para, _ = _para_range(option_count)
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks < min_para - 1:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected >= {min_para - 1})"
    return True, ""
