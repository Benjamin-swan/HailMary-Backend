from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.kkebi.domain.entity.daily_template import DailyTemplate
from app.domains.kkebi.domain.port.daily_template_repository_port import (
    DailyTemplateRepositoryPort,
)
from app.domains.kkebi.infrastructure.mapper.daily_template_mapper import DailyTemplateMapper
from app.domains.kkebi.infrastructure.orm.daily_template_orm import DailyTemplateORM


class DailyTemplateRepository(DailyTemplateRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_keys(self, sipseong: str, branch_rel: str) -> DailyTemplate | None:
        result = await self._session.execute(
            select(DailyTemplateORM).where(
                DailyTemplateORM.sipseong == sipseong,
                DailyTemplateORM.branch_rel == branch_rel,
            )
        )
        orm = result.scalar_one_or_none()
        return DailyTemplateMapper.to_entity(orm) if orm else None

    async def save(self, template: DailyTemplate) -> DailyTemplate:
        orm = DailyTemplateMapper.to_orm(template)
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return DailyTemplateMapper.to_entity(orm)

    async def list_all(self) -> list[DailyTemplate]:
        result = await self._session.execute(select(DailyTemplateORM))
        return [DailyTemplateMapper.to_entity(o) for o in result.scalars().all()]
