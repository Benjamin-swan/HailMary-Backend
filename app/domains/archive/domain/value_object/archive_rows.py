from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaidArchiveRow:
    """보관함의 연우/도윤 결제 결과 한 줄 (payments × paid_reports 조인 결과)."""

    character: str  # "yeonwoo" | "doyoon"
    order_id: str
    share_code: str | None  # 결과지 미합성 시 None (재접속 링크 불가)
    approved_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class KkebiArchiveRow:
    """보관함의 깨비 일일운세 당일 저장본 요약."""

    cycle_id: str
    summary: str | None
