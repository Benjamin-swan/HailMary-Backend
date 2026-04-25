from app.domains.user.domain.entity.saju_result import SajuResult
from app.domains.user.infrastructure.orm.saju_result_orm import SajuResultORM


class SajuResultMapper:
    @staticmethod
    def to_orm(entity: SajuResult) -> SajuResultORM:
        return SajuResultORM(
            id=entity.id,
            user_id=entity.user_id,
            fortuneteller_request=entity.fortuneteller_request,
            fortuneteller_response=entity.fortuneteller_response,
        )

    @staticmethod
    def to_entity(orm: SajuResultORM) -> SajuResult:
        return SajuResult(
            id=orm.id,
            user_id=orm.user_id,
            fortuneteller_request=dict(orm.fortuneteller_request),
            fortuneteller_response=dict(orm.fortuneteller_response),
        )
