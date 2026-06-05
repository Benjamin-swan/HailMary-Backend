"""쿠폰 검증 UseCase — "적용" 버튼용. 읽기 전용, DB 변경 없음.

참고: 검증 결과는 안내용일 뿐, 진짜 1회용 보증은 리뎀션의 원자적 소진이 한다
(검증 ~ 리뎀션 사이 TOCTOU 는 redeem_if_active 가 흡수).
"""

from __future__ import annotations

from app.domains.payment.application.response.validate_coupon_response import (
    ValidateCouponResponse,
)
from app.domains.payment.domain.port.coupon_repository_port import (
    CouponRepositoryPort,
)
from app.domains.payment.domain.service.coupon_code_generator import (
    normalize_coupon_code,
)

_VALID_MSG = "사용 가능한 쿠폰입니다."
_INVALID_MSG = "사용할 수 없는 쿠폰입니다."


class ValidateCouponUseCase:
    def __init__(self, *, coupon_repo: CouponRepositoryPort) -> None:
        self._coupon_repo = coupon_repo

    async def execute(self, *, code: str) -> ValidateCouponResponse:
        coupon = await self._coupon_repo.find_by_code(normalize_coupon_code(code))
        if coupon is not None and coupon.is_redeemable():
            return ValidateCouponResponse(valid=True, message=_VALID_MSG)
        # 없음/소진을 구분 노출하지 않음 (코드 추측 방어).
        return ValidateCouponResponse(valid=False, message=_INVALID_MSG)
