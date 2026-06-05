"""도윤 P-0 0-5 분석 진입 요약 — AI prompt builder.

호출자: generate_p0_diagnosis_usecase. 입력 facts는 doyoon_p0_intro.get_doyoon_p0_facts.

전략: 룰 합성 결과를 *기반 텍스트*로 AI에 전달 → AI가 같은 사실값을 보존하면서
표현·연결사·문장 길이를 다양화. 환각 위험 최소 (수치를 만들 필요 없음, 보존만).

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
    '- 존댓말 사용, "{user_name}님" 호명 (단락 1에서 1회)\n'
    "- 데이터는 근거로만 쓰고 설명은 일상어로 — 어려운 개념은 먼저 쉬운 말로 풀어준다\n"
    "- 따뜻함은 절제하되 기계적이지 않게, 분석 끝에 사람을 향한 한 줄을 남긴다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n"
    '- "운명", "인연이 ~한다" 같은 비결정론적 표현 X\n\n'
    "[사실값 보존 — 절대 변경 금지]\n"
    "참조 데이터에 박힌 다음 값들은 *변경, 누락, 풀어쓰기, 약어화* 모두 금지:\n"
    "- 사용자 이름 ({user_name})\n"
    "- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})\n"
    "- 오행 한자 ({excess_ohang_hanja}, {lack_ohang_hanja})\n"
    "출력 텍스트에 위 문자열들이 그대로 포함돼야 합니다.\n\n"
    "[수치 금지]\n"
    "백분위·퍼센트·접촉률 같은 숫자 통계는 절대 쓰지 마세요. 오행 과다·부족은 "
    '"뚜렷하게 과다", "눈에 띄게 부족"처럼 질적 강도로만 표현합니다.\n\n'
    "[구성] 4 단락, 단락 사이 빈 줄 1개, 총 220~340자\n"
    "1. 호명 + 데이터 정리 완료 신호 (1문장)\n"
    "2. 일간 진단 + 강점 (2문장)\n"
    "3. 핵심 리스크 2개(과다·부족 오행)와 그 영향을 일상어로 (3문장)\n"
    "4. 다음 장 안내 (1문장)\n\n"
    "[출력]\n"
    "4단락 텍스트만 출력. 메타 설명·주석·헤더·코드블록 금지.\n"
)


_USER_PROMPT_TPL = """\
다음 사용자의 P-0 분석 진입 요약을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- excess_ohang_hanja: {excess_ohang_hanja}
- lack_ohang_hanja: {lack_ohang_hanja}

[참고 문구 — 일간 강점 설명]
{ilgan_para_2}

[룰 합성 기반 텍스트 — 이걸 *기반으로* 같은 사실값을 모두 보존한 채 표현을 다양화하세요. \
그대로 복붙은 금지 (연결사·문장 길이·구성 다양화). 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값을 모두 포함하는 4단락 220~340자 텍스트를 작성하세요.
"""


def build_p0_diagnosis_prompt(facts: dict[str, str]) -> tuple[str, str]:
    """facts dict → (system_prompt, user_prompt) 튜플 반환.

    Args:
        facts: doyoon_p0_intro.get_doyoon_p0_facts() 반환 dict.
               필수 키 12개. 누락 시 KeyError.

    Returns:
        (system_prompt, user_prompt). system 안에 user_name도 박힘 (호명 인지용).

    Raises:
        KeyError: facts에 필수 키 누락.
    """
    required_keys = {
        "user_name",
        "ilgan_full",
        "ilgan_hanja",
        "excess_ohang_hanja",
        "lack_ohang_hanja",
        "ilgan_para_2",
        "rule_text",
    }
    missing = required_keys - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")

    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ilgan_hanja=facts["ilgan_hanja"],
        excess_ohang_hanja=facts["excess_ohang_hanja"],
        lack_ohang_hanja=facts["lack_ohang_hanja"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in required_keys})
    return system, user


# ── 출력 검증 ─────────────────────────────────────────────────────


_MIN_LENGTH = 180
_MAX_LENGTH = 500


def validate_p0_diagnosis(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    """AI 출력 텍스트가 facts의 사실값을 모두 보존했는지 검증.

    실패 시 (False, 사유) — 사유는 로그용 (사용자 이름 마스킹).
    성공 시 (True, "").

    검증 단계 (CLAUDE.md 마스킹 룰 — user_name은 로그에 평문 X):
        1. 길이 _MIN_LENGTH~_MAX_LENGTH
        2. user_name 포함
        3. ilgan_full + ilgan_hanja 포함
        4. excess_ohang_hanja 포함
        5. lack_ohang_hanja 포함
        6. 4단락 구조 (\\n\\n 정확히 3회)

    수치(백분위·접촉률)는 2026-06-05 폐기 — 더 이상 검증하지 않음.
    """
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"

    user_name = facts["user_name"]
    if user_name not in text:
        return False, "user_name missing"

    for key in ("ilgan_full", "ilgan_hanja"):
        if facts[key] not in text:
            return False, f"{key} missing: {facts[key]!r}"

    if facts["excess_ohang_hanja"] not in text:
        return False, f"excess_ohang_hanja missing: {facts['excess_ohang_hanja']!r}"
    if facts["lack_ohang_hanja"] not in text:
        return False, f"lack_ohang_hanja missing: {facts['lack_ohang_hanja']!r}"

    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 3:
        return False, f"paragraph structure invalid: {paragraph_breaks} breaks (expected 3)"

    return True, ""
