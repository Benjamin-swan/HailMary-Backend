from typing import Protocol

from app.domains.kkebi.domain.entity.daily_template import DailyTemplate


class DailyTemplateRepositoryPort(Protocol):
    async def find_by_keys(self, sipseong: str, branch_rel: str) -> DailyTemplate | None:
        ...

    async def save(self, template: DailyTemplate) -> DailyTemplate:
        ...

    async def list_all(self) -> list[DailyTemplate]:
        ...
