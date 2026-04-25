"""
설문 슬러그 카탈로그.

DB에는 슬러그 문자열만 저장되고, 의미 해석(label, intent)은 이 파일이 유일한 소스다.
AI 도메인에서 Claude 프롬프트를 조립할 때 expand_slugs()를 호출해 intent 문장을 주입한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SurveyOption:
    label: str   # 프론트 화면에 표시하는 한국어
    intent: str  # Claude 프롬프트에 주입할 맥락 문장


@dataclass(frozen=True)
class ExpandedSlug:
    slug: str
    label: str
    intent: str
    known: bool


_V1: Final[dict[str, dict[str, SurveyOption]]] = {
    "step1": {
        "waiting_new": SurveyOption(
            label="새로운 인연을 기다려요",
            intent="싱글 상태로 적극적으로 새 관계를 찾는 중",
        ),
        "crushing": SurveyOption(
            label="썸 타는 중이에요",
            intent="관계 정의 이전 단계, 일방/쌍방 호감을 탐색 중",
        ),
        "in_relationship": SurveyOption(
            label="연애 중이에요",
            intent="현재 교제 중이며 관계 지속 또는 발전을 고민 중",
        ),
        "missing_ex": SurveyOption(
            label="헤어진 연인이 그리워요",
            intent="이별 후 재결합 또는 미련을 정리하는 단계",
        ),
    },
    "step2": {
        "soulmate": SurveyOption(
            label="내 운명의 상대",
            intent="이상적인 파트너의 성향과 유형을 알고 싶음",
        ),
        "timing": SurveyOption(
            label="다음 인연의 시기",
            intent="언제 새 인연이 찾아오는지 시간축 예측을 원함",
        ),
        "compatibility": SurveyOption(
            label="현재 인연과의 궁합",
            intent="특정 상대와의 적합성과 장기 전망을 판단받고 싶음",
        ),
        "patterns": SurveyOption(
            label="내 연애 패턴의 본질",
            intent="반복되는 자신의 연애 패턴과 그 근원을 진단받고 싶음",
        ),
    },
}

SURVEY_CATALOG: Final[dict[str, dict[str, dict[str, SurveyOption]]]] = {
    "v1": _V1,
}


def expand_slugs(version: str, step: str, slugs: list[str]) -> list[ExpandedSlug]:
    """슬러그 배열을 label + intent 구조로 확장한다. 미등록 슬러그는 known=False로 반환."""
    step_catalog = SURVEY_CATALOG.get(version, {}).get(step, {})
    result: list[ExpandedSlug] = []
    for slug in slugs:
        option = step_catalog.get(slug)
        if option:
            result.append(ExpandedSlug(slug=slug, label=option.label, intent=option.intent, known=True))
        else:
            result.append(ExpandedSlug(slug=slug, label=slug, intent="(미등록 슬러그)", known=False))
    return result
