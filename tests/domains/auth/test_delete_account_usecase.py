"""DeleteAccountUseCase 단위 테스트 (HM-BE-82).

대상:
    1. 삭제 호출이 deletion 포트로 위임되는지
    2. 멱등 — 없는 계정도 예외 없이 통과
"""
from app.domains.auth.application.usecase.delete_account_usecase import (
    DeleteAccountUseCase,
)


class FakeDeletion:
    def __init__(self, exists: bool = True) -> None:
        self._exists = exists
        self.called_with: int | None = None

    async def delete_account(self, account_id: int) -> bool:
        self.called_with = account_id
        return self._exists


async def test_delete_delegates() -> None:
    fake = FakeDeletion(exists=True)
    await DeleteAccountUseCase(deletion=fake).execute(7)
    assert fake.called_with == 7


async def test_delete_idempotent_when_missing() -> None:
    fake = FakeDeletion(exists=False)
    # 없는 계정도 예외 없이 통과 (멱등)
    await DeleteAccountUseCase(deletion=fake).execute(999)
    assert fake.called_with == 999
