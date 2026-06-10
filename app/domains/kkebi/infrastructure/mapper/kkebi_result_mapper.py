from app.domains.kkebi.domain.entity.kkebi_result import KkebiResult
from app.domains.kkebi.infrastructure.orm.kkebi_result_orm import KkebiResultORM


class KkebiResultMapper:
    @staticmethod
    def to_orm(entity: KkebiResult) -> KkebiResultORM:
        return KkebiResultORM(
            id=entity.id,
            account_id=entity.account_id,
            cycle_id=entity.cycle_id,
            name=entity.name,
            result=entity.result,
        )

    @staticmethod
    def to_entity(orm: KkebiResultORM) -> KkebiResult:
        return KkebiResult(
            id=orm.id,
            account_id=orm.account_id,
            cycle_id=orm.cycle_id,
            name=orm.name,
            result=orm.result,
            created_at=orm.created_at,
        )
