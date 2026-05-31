from app.domains.kkebi.domain.entity.daily_template import DailyTemplate
from app.domains.kkebi.infrastructure.orm.daily_template_orm import DailyTemplateORM


class DailyTemplateMapper:
    @staticmethod
    def to_orm(entity: DailyTemplate) -> DailyTemplateORM:
        return DailyTemplateORM(
            id=entity.id,
            sipseong=entity.sipseong,
            branch_rel=entity.branch_rel,
            body=entity.body,
        )

    @staticmethod
    def to_entity(orm: DailyTemplateORM) -> DailyTemplate:
        return DailyTemplate(
            id=orm.id,
            sipseong=orm.sipseong,
            branch_rel=orm.branch_rel,
            body=orm.body,
            created_at=orm.created_at,
        )
