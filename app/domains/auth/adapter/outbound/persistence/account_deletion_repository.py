"""회원탈퇴 cascade — 계정 + 귀속 데이터 정리 (cross-domain write).

결제 기록(payments)은 전자상거래법상 보관 의무가 있어 삭제하지 않고 account_id만 NULL.
깨비 저장본은 개인 데이터라 삭제. archive_repository 와 같은 cross-domain adapter 패턴.
"""
from __future__ import annotations

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.domain.port.account_deletion_port import AccountDeletionPort
from app.domains.auth.infrastructure.orm.account_orm import AccountORM
from app.domains.kkebi.infrastructure.orm.kkebi_result_orm import KkebiResultORM
from app.domains.payment.infrastructure.orm.payment_orm import PaymentORM
from app.domains.user.infrastructure.orm.user_orm import UserORM


class AccountDeletionRepository(AccountDeletionPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def delete_account(self, account_id: int) -> bool:
        # 1. 깨비 저장본 삭제 (FK NOT NULL — 먼저 제거)
        await self._session.execute(
            delete(KkebiResultORM).where(KkebiResultORM.account_id == account_id)
        )
        # 2. 결제/유저 언링크 (결제 기록은 법적 보관 — 행 유지, account_id만 NULL)
        await self._session.execute(
            update(PaymentORM)
            .where(PaymentORM.account_id == account_id)
            .values(account_id=None)
        )
        await self._session.execute(
            update(UserORM)
            .where(UserORM.account_id == account_id)
            .values(account_id=None)
        )
        # 3. 계정 삭제 (rowcount로 존재 여부 판정)
        result = await self._session.execute(
            delete(AccountORM).where(AccountORM.id == account_id)
        )
        await self._session.flush()
        return bool(getattr(result, "rowcount", 0))
