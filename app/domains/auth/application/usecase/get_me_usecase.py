from app.domains.auth.application.response.account_profile_response import (
    AccountProfileResponse,
)
from app.domains.auth.domain.port.account_repository_port import AccountRepositoryPort


class GetMeUseCase:
    """JWT로 식별된 계정의 프로필 + 마지막 사용값 조회."""

    def __init__(self, *, account_repo: AccountRepositoryPort) -> None:
        self._account_repo = account_repo

    async def execute(self, account_id: int) -> AccountProfileResponse:
        account = await self._account_repo.find_by_id(account_id)
        if account is None:
            # 토큰은 유효하나 계정이 삭제된 경우 — 인증 실패로 취급
            raise ValueError("계정을 찾을 수 없습니다")
        return AccountProfileResponse.from_account(account)
