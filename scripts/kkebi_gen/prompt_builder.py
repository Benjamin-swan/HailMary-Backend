"""70조합(십성 10 × 지지관계 7) 통째 유저 프롬프트 생성.

시스템 프롬프트(system_prompt.txt)에 명리 가이드·금지·스키마가 다 들어있으므로
유저 프롬프트는 "어느 조합인지 + 영역/시간대 무드 힌트"만 짧게 전달한다.
"""
from __future__ import annotations

from scripts.kkebi_pilot.matrix import (
    AREA_KOREAN,
    AREAS,
    TIME_KOREAN,
    TIME_SLOTS,
    mood3_from_score,
    score_area,
    score_time,
    score_total,
)

# 십성 10종 · 지지관계 7종
SIPSEONG = ["비견", "겁재", "식신", "상관", "편재", "정재", "편관", "정관", "편인", "정인"]
BRANCH_REL = ["합", "충", "형", "파", "해", "동주", "보통"]

MOOD_HINT_KR = {"good": "좋은 흐름", "mid": "보통 흐름"}


def iter_combos():
    """70개 (sipseong, branch_rel) 조합."""
    for ss in SIPSEONG:
        for br in BRANCH_REL:
            yield ss, br


def build_user_prompt(sipseong: str, branch_rel: str) -> str:
    total = score_total(sipseong, branch_rel)
    total_hint = MOOD_HINT_KR[mood3_from_score(total)]

    area_lines = []
    for area in AREAS:
        m = mood3_from_score(score_area(sipseong, area))
        area_lines.append(f"  - {AREA_KOREAN[area]}({area}): {MOOD_HINT_KR[m]}")
    time_lines = []
    for ts in TIME_SLOTS:
        m = mood3_from_score(score_time(sipseong, ts))
        time_lines.append(f"  - {TIME_KOREAN[ts]}({ts}): {MOOD_HINT_KR[m]}")

    return f"""아래 한 사람의 오늘 하루 운세 결과지를 시스템 규칙대로 JSON 한 덩어리로 작성하라.

[이 사람의 오늘 기운 — 내부 추론용]
- 십성: {sipseong}
- 지지관계: {branch_rel}
- 하루 전체 톤: {total_hint}

[영역별 무드 힌트 — 톤 차등화에 반영]
{chr(10).join(area_lines)}

[시간대별 무드 힌트]
{chr(10).join(time_lines)}

규칙(도메인어 금지·과잉구체 금지·바넘·슬롯별 길이/어미·JSON only)은 시스템 프롬프트를 그대로 따른다.
순수 JSON만 출력."""
