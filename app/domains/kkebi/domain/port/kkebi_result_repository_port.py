from __future__ import annotations

from typing import Any, Protocol

from app.domains.kkebi.domain.entity.kkebi_result import KkebiResult


class KkebiResultRepositoryPort(Protocol):
    async def save_today(
        self, *, account_id: int, cycle_id: str, name: str, result: dict[str, Any]
    ) -> None:
        """오늘 결과 저장 + 해당 계정의 과거 cycle 행 삭제(당일만 보관)."""
        ...

    async def find_today(
        self, *, account_id: int, cycle_id: str
    ) -> KkebiResult | None: ...
