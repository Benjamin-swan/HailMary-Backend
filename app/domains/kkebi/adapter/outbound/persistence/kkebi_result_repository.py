from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.kkebi.domain.entity.kkebi_result import KkebiResult
from app.domains.kkebi.domain.port.kkebi_result_repository_port import (
    KkebiResultRepositoryPort,
)
from app.domains.kkebi.infrastructure.mapper.kkebi_result_mapper import KkebiResultMapper
from app.domains.kkebi.infrastructure.orm.kkebi_result_orm import KkebiResultORM


class KkebiResultRepository(KkebiResultRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_today(
        self, *, account_id: int, cycle_id: str, name: str, result: dict[str, Any]
    ) -> None:
        # 당일만 보관 — 과거 cycle 행 제거 (자정 지나면 어차피 today 조회가 404)
        await self._session.execute(
            delete(KkebiResultORM).where(
                KkebiResultORM.account_id == account_id,
                KkebiResultORM.cycle_id != cycle_id,
            )
        )
        # 오늘 row upsert (재조회/재계산 시 덮어쓰기)
        existing = (
            await self._session.execute(
                select(KkebiResultORM).where(
                    KkebiResultORM.account_id == account_id,
                    KkebiResultORM.cycle_id == cycle_id,
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            existing.name = name
            existing.result = result
        else:
            self._session.add(
                KkebiResultORM(
                    account_id=account_id,
                    cycle_id=cycle_id,
                    name=name,
                    result=result,
                )
            )
        await self._session.flush()

    async def find_today(
        self, *, account_id: int, cycle_id: str
    ) -> KkebiResult | None:
        orm = (
            await self._session.execute(
                select(KkebiResultORM).where(
                    KkebiResultORM.account_id == account_id,
                    KkebiResultORM.cycle_id == cycle_id,
                )
            )
        ).scalar_one_or_none()
        return KkebiResultMapper.to_entity(orm) if orm else None
