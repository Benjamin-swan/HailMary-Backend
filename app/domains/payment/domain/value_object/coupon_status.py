from enum import Enum


class CouponStatus(str, Enum):
    """쿠폰 상태. 100% 무료·1회용·무기한 모델이라 두 값으로 충분."""

    ACTIVE = "ACTIVE"      # 미사용 — 리뎀션 가능
    REDEEMED = "REDEEMED"  # 1회용 소진 완료
