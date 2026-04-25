from app.domains.user.domain.entity.survey import Survey
from app.domains.user.infrastructure.orm.survey_orm import SurveyORM


class SurveyMapper:
    @staticmethod
    def to_orm(entity: Survey) -> SurveyORM:
        return SurveyORM(
            id=entity.id,
            user_id=entity.user_id,
            survey_version=entity.survey_version,
            step1_slugs=entity.step1_slugs,
            step2_slugs=entity.step2_slugs,
            step3_text=entity.step3_text,
        )

    @staticmethod
    def to_entity(orm: SurveyORM) -> Survey:
        return Survey(
            id=orm.id,
            user_id=orm.user_id,
            survey_version=orm.survey_version,
            step1_slugs=list(orm.step1_slugs),
            step2_slugs=list(orm.step2_slugs),
            step3_text=orm.step3_text,
        )
