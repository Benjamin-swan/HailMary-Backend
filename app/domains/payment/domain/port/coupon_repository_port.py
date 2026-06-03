from abc import ABC, abstractmethod
from datetime import datetime

from app.domains.payment.domain.entity.coupon import Coupon


class CouponRepositoryPort(ABC):
    @abstractmethod
    async def find_by_code(self, code: str) -> Coupon | None:
        """코드로 쿠폰 조회 (검증/조회용, 읽기 전용). 없으면 None."""
        ...

    @abstractmethod
    async def redeem_if_active(
        self,
        *,
        code: str,
        user_id: int,
        order_id: str,
        used_at: datetime,
    ) -> bool:
        """ACTIVE 쿠폰을 원자적으로 REDEEMED 로 전이.

        `UPDATE ... WHERE code=? AND status='ACTIVE'` 단일 쿼리의 rowcount 로 판정.
        성공(내가 소진) 시 True, 이미 소진/없음이면 False — 동시 제출 race 방지.
        """
        ...

    @abstractmethod
    async def save(self, coupon: Coupon) -> Coupon:
        """새 쿠폰 저장 (CLI 발급 스크립트용)."""
        ...
