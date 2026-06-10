from typing import Protocol


class AccountDeletionPort(Protocol):
    async def delete_account(self, account_id: int) -> bool:
        """계정 + 귀속 데이터 정리. 존재하지 않으면 False.

        - kkebi_results: 삭제 (FK NOT NULL)
        - payments / users: account_id NULL 언링크 (결제 기록 등은 법적 보관)
        - accounts: 삭제
        """
        ...
