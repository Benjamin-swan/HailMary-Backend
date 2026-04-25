from typing import Protocol

from app.domains.user.domain.entity.survey import Survey


class SurveyRepositoryPort(Protocol):
    async def save(self, survey: Survey) -> Survey: ...
    async def find_by_user_id(self, user_id: int) -> Survey | None: ...
