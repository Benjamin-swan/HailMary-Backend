from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class KkebiResult:
    """로그인 사용자의 깨비 일일운세 저장본.

    당일(cycle_id)만 보관 — 자정(KST) 지나 다음 cycle이 되면 보관함에서 자연 소멸.
    result에는 DailyFortuneResponse 직렬화본을 그대로 담아 '다시보기'에서 복원한다.
    account 소유 데이터이므로 본인 이름은 보관 가능(공유 Redis 캐시의 PII 금지와는 다름).
    """

    account_id: int
    cycle_id: str  # KST YYYYMMDD
    name: str
    result: dict[str, Any] = field(default_factory=dict)
    id: int | None = None
    created_at: datetime | None = None
