from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.domain.entity.saju_result import SajuResult
from app.domains.user.infrastructure.mapper.saju_result_mapper import SajuResultMapper
from app.domains.user.infrastructure.orm.saju_result_orm import SajuResultORM


class SajuResultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, result: SajuResult) -> SajuResult:
        orm = SajuResultMapper.to_orm(result)
        self._session.add(orm)
        await self._session.flush()
        return SajuResultMapper.to_entity(orm)

    async def find_by_user_id(self, user_id: int) -> SajuResult | None:
        stmt = select(SajuResultORM).where(SajuResultORM.user_id == user_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return SajuResultMapper.to_entity(orm) if orm else None
