from typing import Protocol

from app.domains.user.domain.entity.user import User


class UserRepositoryPort(Protocol):
    async def save(self, user: User) -> User: ...
    async def find_by_id(self, user_id: int) -> User | None: ...
