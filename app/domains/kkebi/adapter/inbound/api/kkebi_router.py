from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.kkebi.application.request.kkebi_fortune_request import KkebiFortuneRequest
from app.domains.kkebi.application.response.daily_fortune_response import DailyFortuneResponse
from app.domains.kkebi.application.usecase.get_daily_fortune_usecase import (
    GetDailyFortuneUseCase,
)
from app.infrastructure.external.fortuneteller.client import FortuneTellerError

router = APIRouter(prefix="/api/kkebi", tags=["kkebi"])


# main.py에서 app.dependency_overrides로 교체된다.
def get_daily_fortune_usecase() -> GetDailyFortuneUseCase:
    raise NotImplementedError


@router.post("/fortune", response_model=DailyFortuneResponse)
async def get_daily_fortune(
    body: KkebiFortuneRequest,
    usecase: GetDailyFortuneUseCase = Depends(get_daily_fortune_usecase),
) -> DailyFortuneResponse:
    try:
        return await usecase.execute(body)
    except FortuneTellerError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
