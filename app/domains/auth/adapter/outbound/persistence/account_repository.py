from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.domain.entity.account import Account
from app.domains.auth.domain.port.account_repository_port import (
    AccountAlreadyExistsError,
    AccountRepositoryPort,
)
from app.domains.auth.domain.value_object.provider import Provider
from app.domains.auth.infrastructure.mapper.account_mapper import AccountMapper
from app.domains.auth.infrastructure.orm.account_orm import AccountORM


class AccountRepository(AccountRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, account: Account) -> Account:
        orm = AccountMapper.to_orm(account)
        # SAVEPOINT로 감싼다 — UNIQUE 충돌(동시 첫 로그인 레이스) 시 nested만 롤백되고
        # 바깥 요청 트랜잭션은 살아남아 UseCase가 재조회→update로 합류할 수 있다.
        try:
            async with self._session.begin_nested():
                self._session.add(orm)
                await self._session.flush()
        except IntegrityError as e:
            raise AccountAlreadyExistsError(
                f"이미 존재하는 계정 (provider={account.provider.value})"
            ) from e
        # created_at이 server_default — flush 후 refresh 필수 (SQLAlchemy async 가드)
        await self._session.refresh(orm)
        return AccountMapper.to_entity(orm)

    async def update(self, account: Account) -> Account:
        if account.id is None:
            raise ValueError("update 대상 계정에 id가 없습니다")
        result = await self._session.execute(
            select(AccountORM).where(AccountORM.id == account.id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            raise ValueError(f"계정이 존재하지 않습니다 (id={account.id})")
        AccountMapper.apply_to_orm(account, orm)
        await self._session.flush()
        return AccountMapper.to_entity(orm)

    async def find_by_id(self, account_id: int) -> Account | None:
        result = await self._session.execute(
            select(AccountORM).where(AccountORM.id == account_id)
        )
        orm = result.scalar_one_or_none()
        return AccountMapper.to_entity(orm) if orm else None

    async def find_by_provider_user(
        self, provider: Provider, provider_user_id: str
    ) -> Account | None:
        result = await self._session.execute(
            select(AccountORM).where(
                AccountORM.provider == provider,
                AccountORM.provider_user_id == provider_user_id,
            )
        )
        orm = result.scalar_one_or_none()
        return AccountMapper.to_entity(orm) if orm else None
