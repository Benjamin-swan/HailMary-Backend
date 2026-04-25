from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SajuResult:
    user_id: int
    fortuneteller_request: dict  # type: ignore[type-arg]
    fortuneteller_response: dict  # type: ignore[type-arg]
    id: int | None = None
    created_at: datetime | None = None
