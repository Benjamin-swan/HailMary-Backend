from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.auth.adapter.inbound.api.auth_router import (
    get_current_account_id,
    get_optional_account_id,
)
from app.domains.kkebi.application.request.kkebi_fortune_request import KkebiFortuneRequest
from app.domains.kkebi.application.response.daily_fortune_response import DailyFortuneResponse
from app.domains.kkebi.application.usecase.get_daily_fortune_usecase import (
    GetDailyFortuneUseCase,
)
from app.domains.kkebi.application.usecase.get_saved_daily_result_usecase import (
    GetSavedDailyResultUseCase,
)
from app.infrastructure.external.fortuneteller.client import FortuneTellerError

router = APIRouter(prefix="/api/kkebi", tags=["kkebi"])


# main.py에서 app.dependency_overrides로 교체된다.
def get_daily_fortune_usecase() -> GetDailyFortuneUseCase:
    raise NotImplementedError


def get_saved_daily_result_usecase() -> GetSavedDailyResultUseCase:
    raise NotImplementedError


@router.post("/fortune", response_model=DailyFortuneResponse)
async def get_daily_fortune(
    body: KkebiFortuneRequest,
    account_id: int | None = Depends(get_optional_account_id),
    usecase: GetDailyFortuneUseCase = Depends(get_daily_fortune_usecase),
) -> DailyFortuneResponse:
    # 비로그인이면 account_id=None → 기존 동작 그대로. 로그인이면 결과 저장(다시보기).
    try:
        return await usecase.execute(body, account_id)
    except FortuneTellerError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/result/today", response_model=DailyFortuneResponse)
async def get_saved_today(
    account_id: int = Depends(get_current_account_id),
    usecase: GetSavedDailyResultUseCase = Depends(get_saved_daily_result_usecase),
) -> DailyFortuneResponse:
    """보관함 '다시보기' — 오늘 저장된 깨비 운세. 없으면 404(자정 지나 소멸)."""
    try:
        return await usecase.execute(account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
