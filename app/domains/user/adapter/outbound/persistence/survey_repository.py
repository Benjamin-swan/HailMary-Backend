from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.domain.entity.survey import Survey
from app.domains.user.infrastructure.mapper.survey_mapper import SurveyMapper
from app.domains.user.infrastructure.orm.survey_orm import SurveyORM


class SurveyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, survey: Survey) -> Survey:
        orm = SurveyMapper.to_orm(survey)
        self._session.add(orm)
        await self._session.flush()
        return SurveyMapper.to_entity(orm)

    async def find_by_user_id(self, user_id: int) -> Survey | None:
        result = await self._session.execute(
            select(SurveyORM).where(SurveyORM.user_id == user_id)
        )
        orm = result.scalar_one_or_none()
        return SurveyMapper.to_entity(orm) if orm else None
