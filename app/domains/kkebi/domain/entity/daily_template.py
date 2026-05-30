from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DailyTemplate:
    """깨비 일일사주 본문 템플릿 1장 = (십성 × 지지관계) 조합.

    body 구조 (AI 생성, 도메인어 없는 완성 본문):
      {
        "headline": str,
        "areas": {love|work|money|health|study: {summary,bok,gyeong,jo}},
        "timeFlow": {morning|afternoon|night: {comment,tip}}
      }
    점수/무드/lucky 는 룰로 조회 시 계산하므로 저장하지 않는다.
    """
    sipseong: str
    branch_rel: str
    body: dict  # type: ignore[type-arg]
    id: int | None = None
    created_at: datetime | None = None
