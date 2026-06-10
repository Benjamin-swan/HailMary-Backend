from typing import Protocol

from app.domains.auth.domain.entity.account import Account
from app.domains.auth.domain.value_object.provider import Provider


class AccountAlreadyExistsError(Exception):
    """동시 첫 로그인 레이스 — 같은 (provider, provider_user_id)가 이미 INSERT됨.

    구현체(Repository)가 DB UNIQUE 위반(IntegrityError)을 이 도메인 예외로 번역.
    UseCase는 이를 잡아 재조회 후 update 경로로 합류한다 (upsert-with-retry).
    """


class AccountRepositoryPort(Protocol):
    async def save(self, account: Account) -> Account: ...
    async def update(self, account: Account) -> Account: ...
    async def find_by_id(self, account_id: int) -> Account | None: ...
    async def find_by_provider_user(
        self, provider: Provider, provider_user_id: str
    ) -> Account | None: ...
