from datetime import datetime
from typing import Any, cast

from sqlalchemy import CursorResult, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.payment.domain.entity.coupon import Coupon
from app.domains.payment.domain.port.coupon_repository_port import (
    CouponRepositoryPort,
)
from app.domains.payment.domain.value_object.coupon_status import CouponStatus
from app.domains.payment.infrastructure.mapper.coupon_mapper import CouponMapper
from app.domains.payment.infrastructure.orm.coupon_orm import CouponORM


class CouponRepository(CouponRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_code(self, code: str) -> Coupon | None:
        result = await self._session.execute(
            select(CouponORM).where(CouponORM.code == code),
        )
        orm = result.scalar_one_or_none()
        return CouponMapper.to_entity(orm) if orm else None

    async def redeem_if_active(
        self,
        *,
        code: str,
        user_id: int,
        order_id: str,
        used_at: datetime,
    ) -> bool:
        """단일 조건부 UPDATE 의 rowcount 로 1회용 보장.

        동시 제출/double-submit 은 DB 행잠금으로 직렬화되어 한쪽만 rowcount==1.
        """
        result = await self._session.execute(
            update(CouponORM)
            .where(
                CouponORM.code == code,
                CouponORM.status == CouponStatus.ACTIVE,
            )
            .values(
                status=CouponStatus.REDEEMED,
                used_at=used_at,
                used_by_user_id=user_id,
                used_order_id=order_id,
            )
        )
        # UPDATE 는 CursorResult 를 반환 — rowcount 로 소진 성공(==1) 판정.
        return cast("CursorResult[Any]", result).rowcount == 1

    async def save(self, coupon: Coupon) -> Coupon:
        orm = CouponMapper.to_orm(coupon)
        self._session.add(orm)
        await self._session.flush()
        return CouponMapper.to_entity(orm)
