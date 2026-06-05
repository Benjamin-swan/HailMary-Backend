"""도윤 P-6 4-1 인연 프로파일 — AI prompt + validate."""

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
    '- 존댓말 사용, "{user_name}님" 호명 (마지막 단락에서 1회)\n'
    "- 어떤 사람과 잘 맞는지, 그 사람의 모습과 성향, 함께일 때 안정되는 이유를"
    " 그려주듯 설명한다 — 잘 맞음을 점수표가 아니라 사람 이야기로 풀어준다\n"
    "- 4장 도입부답게 온기를 약간 더 싣되, 과장하지 않는다\n\n"
    + DOYOON_FORBIDDEN_BLOCK + "\n\n"
    "[사실값 보존]\n"
    "- {user_name}, {ilgan_full}({ilgan_hanja})\n"
    "- 잘 맞는 상위 {pct_value}\n"
    "- 키 {height_distribution_pct} / 첫인상 신호 {profile_signal_pct}"
    " / 감정 기복 {emotional_stability_multiplier}\n"
    "- 안정감 {stability_high_multiplier} / 잘 맞는 정도 {compatibility_pct}"
    " / 평균 {avg_compatibility_baseline} / 평균보다 {compatibility_lift}\n"
    "- 채워주는 오행 {ohang_lack}({ohang_lack_hanja})\n\n"
    "[구성] 4단락, 총 360~620자\n"
    "1. 잘 맞는 상위 % 도입\n"
    "2. 겉모습 특징 4가지\n"
    "3. 성향과 안정감, 어울리는 직업군\n"
    "4. 채워주는 오행과 잘 맞는 이유 + {user_name}님 호명\n\n"
    "[출력] 4단락만.\n"
)

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- ohang_lack: {ohang_lack}
- ohang_lack_hanja: {ohang_lack_hanja}
- pct_value: {pct_value}
- height_distribution_pct: {height_distribution_pct}
- profile_signal_pct: {profile_signal_pct}
- emotional_stability_multiplier: {emotional_stability_multiplier}
- stability_high_multiplier: {stability_high_multiplier}
- compatibility_pct: {compatibility_pct}
- avg_compatibility_baseline: {avg_compatibility_baseline}
- compatibility_lift: {compatibility_lift}

[기반]
{rule_text}

[요청] 4단락 360~620자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "ohang_lack", "ohang_lack_hanja", "pct_value",
    "height_distribution_pct", "profile_signal_pct",
    "emotional_stability_multiplier", "stability_high_multiplier",
    "compatibility_pct", "avg_compatibility_baseline", "compatibility_lift",
    "rule_text",
}


def build_p6_profile_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 320
_MAX_LENGTH = 700


def validate_p6_profile(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "ilgan_full", "pct_value", "compatibility_pct",
              "ohang_lack_hanja"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 3:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 3)"
    return True, ""
