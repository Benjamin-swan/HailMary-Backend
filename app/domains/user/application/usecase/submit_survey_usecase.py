from app.domains.user.application.request.submit_survey_request import SubmitSurveyRequest
from app.domains.user.application.response.survey_response import SurveyResponse
from app.domains.user.domain.entity.survey import Survey
from app.domains.user.domain.entity.user import User
from app.domains.user.domain.port.saju_result_repository_port import SajuResultRepositoryPort
from app.domains.user.domain.port.survey_repository_port import SurveyRepositoryPort


class SubmitSurveyUseCase:
    def __init__(
        self,
        survey_repo: SurveyRepositoryPort,
        saju_result_repo: SajuResultRepositoryPort,
    ) -> None:
        self._survey_repo = survey_repo
        self._saju_result_repo = saju_result_repo

    async def execute(self, user: User, request: SubmitSurveyRequest) -> SurveyResponse:
        assert user.id is not None

        saju_result = await self._saju_result_repo.find_by_user_id(user.id)
        if saju_result is None:
            raise ValueError("사주 분석 결과가 없습니다. 먼저 /api/saju/free를 호출하세요.")

        survey = Survey(
            user_id=user.id,
            survey_version=request.survey_version,
            step1_slugs=request.step1,
            step2_slugs=request.step2,
            step3_text=request.step3,
        )
        saved = await self._survey_repo.save(survey)
        assert saved.id is not None
        return SurveyResponse(surveyId=saved.id)
