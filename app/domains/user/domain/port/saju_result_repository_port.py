from typing import Protocol

from app.domains.user.domain.entity.saju_result import SajuResult


class SajuResultRepositoryPort(Protocol):
    async def save(self, result: SajuResult) -> SajuResult: ...
    async def find_by_user_id(self, user_id: int) -> SajuResult | None: ...
