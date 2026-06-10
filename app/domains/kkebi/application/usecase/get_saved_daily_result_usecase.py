from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domains.kkebi.application.response.daily_fortune_response import (
    DailyFortuneResponse,
)
from app.domains.kkebi.domain.port.kkebi_result_repository_port import (
    KkebiResultRepositoryPort,
)
from app.domains.kkebi.domain.service.ganzhi_calendar import cycle_id

_KST = timezone(timedelta(hours=9))


class GetSavedDailyResultUseCase:
    """보관함 '다시보기' — 로그인 사용자의 오늘 깨비 운세 저장본 조회.

    오늘(KST cycle) 저장본이 없으면 ValueError → 라우터 404 → 보관함에서 자연 소멸.
    저장본(result dict)은 DailyFortuneResponse 직렬화본 → 모델로 재파싱해 반환.
    """

    def __init__(self, *, result_repo: KkebiResultRepositoryPort) -> None:
        self._result_repo = result_repo

    async def execute(self, account_id: int) -> DailyFortuneResponse:
        today = cycle_id(datetime.now(_KST).date())
        saved = await self._result_repo.find_today(
            account_id=account_id, cycle_id=today
        )
        if saved is None:
            raise ValueError("오늘 저장된 깨비 운세가 없습니다")
        return DailyFortuneResponse.model_validate(saved.result)
