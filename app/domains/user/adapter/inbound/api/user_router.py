from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.user.adapter.inbound.api.auth import get_current_user
from app.domains.user.application.request.submit_survey_request import SubmitSurveyRequest
from app.domains.user.application.request.submit_user_info_request import SubmitUserInfoRequest
from app.domains.user.application.response.free_result_response import FreeResultResponse
from app.domains.user.application.response.survey_response import SurveyResponse
from app.domains.user.application.usecase.get_free_result_usecase import GetFreeResultUseCase
from app.domains.user.application.usecase.submit_survey_usecase import SubmitSurveyUseCase
from app.domains.user.application.usecase.submit_user_info_usecase import SubmitUserInfoUseCase
from app.domains.user.domain.entity.user import User
from app.infrastructure.external.fortuneteller.client import FortuneTellerError

router = APIRouter(prefix="/api/saju", tags=["saju"])


# main.py에서 app.dependency_overrides로 교체된다.
def get_submit_user_info_usecase() -> SubmitUserInfoUseCase:
    raise NotImplementedError


def get_submit_survey_usecase() -> SubmitSurveyUseCase:
    raise NotImplementedError


def get_free_result_usecase() -> GetFreeResultUseCase:
    raise NotImplementedError


@router.post("/free", response_model=FreeResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_free(
    body: SubmitUserInfoRequest,
    usecase: SubmitUserInfoUseCase = Depends(get_submit_user_info_usecase),
) -> FreeResultResponse:
    try:
        return await usecase.execute(body)
    except FortuneTellerError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/survey", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def submit_survey(
    body: SubmitSurveyRequest,
    current_user: User = Depends(get_current_user),
    usecase: SubmitSurveyUseCase = Depends(get_submit_survey_usecase),
) -> SurveyResponse:
    try:
        return await usecase.execute(current_user, body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/result", response_model=FreeResultResponse)
async def get_free_result(
    current_user: User = Depends(get_current_user),
    usecase: GetFreeResultUseCase = Depends(get_free_result_usecase),
) -> FreeResultResponse:
    try:
        return await usecase.execute(current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
