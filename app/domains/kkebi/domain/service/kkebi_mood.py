"""점수(0~100) → 프론트 kkebiMood 4단계 변환 (순수 Python).

프론트(SajuResult.total.kkebiMood)는 "high"|"mid-high"|"mid"|"low" 4단계.
점수는 70~99 범위에 20/50/30 분포(70대 20% / 80대 50% / 90대 30%)로 설계됨.
밴드를 그 분포에 맞춰 high(90+) 30% / mid-high(80+) 50% / mid(70+) 20%.
floor 70 정책상 'low'는 방어적 분기일 뿐 정상 흐름에선 안 나온다.
프론트 sajuRules.ts::scoreToMood 도 동일 임계(90/80/70)로 맞춘다.
"""
from __future__ import annotations


def to_kkebi_mood(score: int) -> str:
    if score >= 90:
        return "high"
    if score >= 80:
        return "mid-high"
    if score >= 70:
        return "mid"
    return "low"  # 70 미만 — floor 70 정책상 정상 흐름에선 안 나옴
