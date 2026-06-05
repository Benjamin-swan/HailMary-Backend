"""도윤 P-9 6-2 리스크 변수 제거 — AI prompt + validate.

핵심 원칙: *위 카드 표를 풀이하는 톤*. 카드 라벨 (81%·64%·47%)만 사용.
즉시 변수 단독 임팩트(36%)·위험도 % 단순 합산(192→130) 등 카드 외 수치 금지
(QA F-056: 무의미한 합산).
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 2)
- 어휘: 카드, 위험도, 우선순위, 합산, 수렴
- 표준 톤 — 카드 *해석가*

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[★ 핵심 규칙 — 카드 풀이 톤]
사용자 화면 *위쪽 카드 표*에 표시된 사실값만 사용:
- 즉시 · 위험도 81% — 미정리 관계 변수
- 단기 · 위험도 64% — 충동 표현 빈도
- 중기 · 위험도 47% — 동선 단조로움

**카드에 표시되지 않은 별도 수치를 절대 끌어오지 마세요**:
- 즉시 변수 단독 임팩트 (36% 같은) X
- 새 인연 진입률 같은 *추가 사실값 금지*
- 위험도 % 단순 합산(192)·수렴 배수·130 같은 합산 수치 금지 (통계적으로 무의미)
- 카드 라벨 (81%, 64%, 47%)만 사용

[사실값 보존]
- {user_name}, {ilgan_full}
- 카드 라벨: 81%, 64%, 47% (각각 즉시·단기·중기)

[구성] 2 단락, 총 170~310자
1. 카드 3장 정리 + 우선순위 (81% > 64% > 47%)
2. {user_name}님 호명 + 우선순위 행동 (즉시 81%부터 하나씩 정리)

[출력] 2단락만. 메타·헤더 금지.
"""

_USER_PROMPT_TPL = """\
[사실값 — 카드 표시 항목만]
- user_name: {user_name}
- ilgan_full: {ilgan_full}

[카드 표시 라벨 — 답변에 직접 풀이할 것]
- 즉시 · 위험도 81% — 미정리 관계 변수
- 단기 · 위험도 64% — 충동 표현 빈도
- 중기 · 위험도 47% — 동선 단조로움

[기반 룰 텍스트]
{rule_text}

[요청] 2단락 170~310자.
카드 라벨(81%·64%·47%)만 풀이. 단순 합산(192·130)·"새 인연 진입률 36%" 같은 카드 외 수치 금지.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "rule_text",
}


def build_p9_risk_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 150
_MAX_LENGTH = 400

# 카드에 없는 별도 수치 — 답변에 등장 시 fail. 192/130(무의미 합산, F-056)도 차단.
_FORBIDDEN_NUMBERS = ("36%", "35%", "37%", "38%", "192", "130")


def validate_p9_risk(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    # 카드 라벨 — 최소 81% (즉시 — 가장 중요)가 등장해야
    if "81%" not in text:
        return False, "card label 81% missing (immediate risk)"
    # 카드 외 별도 수치 금지 (192·130 무의미 합산 포함)
    for n in _FORBIDDEN_NUMBERS:
        if n in text:
            return False, f"forbidden meta-value: {n!r} (not in card display)"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 1:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
