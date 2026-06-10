from __future__ import annotations

from datetime import time as time_cls

from app.domains.auth.application.request.update_last_used_request import (
    UpdateLastUsedRequest,
)
from app.domains.auth.domain.port.account_repository_port import AccountRepositoryPort
from app.domains.auth.domain.value_object.last_used_profile import LastUsedProfile


class UpdateLastUsedUseCase:
    """로그인 사용자가 설문 제출 시 계정의 '마지막 사용값'을 갱신.

    설문(연우/도윤/깨비) 제출 직후 FE가 fire-and-forget로 호출 — 기존 무료사주/깨비
    엔드포인트는 건드리지 않는다(코어 플로 무영향). time 부분 갱신 규칙은 요청 DTO 참고.
    """

    def __init__(self, *, account_repo: AccountRepositoryPort) -> None:
        self._account_repo = account_repo

    async def execute(self, account_id: int, request: UpdateLastUsedRequest) -> None:
        account = await self._account_repo.find_by_id(account_id)
        if account is None:
            raise ValueError("계정을 찾을 수 없습니다")

        prev = account.last_used
        if request.time is None:
            # 시간 정보 없는 플로(깨비) — 기존 시각 유지
            birth_time = prev.birth_time if prev else None
            birth_time_unknown = prev.birth_time_unknown if prev else True
        elif request.time == "unknown":
            birth_time = None
            birth_time_unknown = True
        else:
            birth_time = time_cls.fromisoformat(request.time)
            birth_time_unknown = False

        account.last_used = LastUsedProfile(
            name=request.name,
            birth_date=request.birth_date(),
            calendar_type=request.calendar,
            birth_time=birth_time,
            birth_time_unknown=birth_time_unknown,
            gender=request.gender,
        )
        await self._account_repo.update(account)
