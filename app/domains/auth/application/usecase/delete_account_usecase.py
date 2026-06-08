from app.domains.auth.domain.port.account_deletion_port import AccountDeletionPort


class DeleteAccountUseCase:
    """회원탈퇴 — 계정 + 귀속 데이터 정리. 멱등(이미 없으면 조용히 성공 취급)."""

    def __init__(self, *, deletion: AccountDeletionPort) -> None:
        self._deletion = deletion

    async def execute(self, account_id: int) -> None:
        await self._deletion.delete_account(account_id)
