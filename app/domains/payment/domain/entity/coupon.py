from dataclasses import dataclass
from datetime import datetime

from app.domains.payment.domain.value_object.coupon_status import CouponStatus


@dataclass
class Coupon:
    """100% 무료 쿠폰 도메인 엔티티 — 1회용, 무기한.

    인스타 후기 대가 / CS 보상 용도. 리뎀션 시 amount=0 결제를 생성해
    PayApp 을 우회하고 유료 결과지 합성을 트리거한다.
    """

    code: str
    status: CouponStatus
    created_at: datetime
    memo: str | None = None              # 용도 메모 (예: "insta_review", "cs_2026_06")
    used_at: datetime | None = None
    used_by_user_id: int | None = None
    used_order_id: str | None = None     # 리뎀션으로 생성된 Payment 추적
    id: int | None = None

    @classmethod
    def issue(cls, *, code: str, created_at: datetime, memo: str | None = None) -> "Coupon":
        """발급(미사용) 상태의 새 쿠폰을 만든다 — CLI 발급 스크립트용."""
        return cls(
            code=code,
            status=CouponStatus.ACTIVE,
            created_at=created_at,
            memo=memo,
        )

    def is_redeemable(self) -> bool:
        return self.status == CouponStatus.ACTIVE
