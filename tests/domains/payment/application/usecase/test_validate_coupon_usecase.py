"""ValidateCouponUseCase 단위 테스트 — 읽기 전용 검증.

대상:
    1. ACTIVE 코드 → valid=True
    2. 없는 코드 → valid=False
    3. 이미 소진된 코드 → valid=False
    4. 읽기 전용 — redeem/save 절대 호출 안 함
    5. 코드 정규화 — 소문자/공백 입력도 매칭
"""

from datetime import UTC, datetime

from app.domains.payment.application.usecase.validate_coupon_usecase import (
    ValidateCouponUseCase,
)
from app.domains.payment.domain.entity.coupon import Coupon
from app.domains.payment.domain.port.coupon_repository_port import (
    CouponRepositoryPort,
)
from app.domains.payment.domain.value_object.coupon_status import CouponStatus


class FakeCouponRepository(CouponRepositoryPort):
    def __init__(self, coupons: list[Coupon] | None = None) -> None:
        self._by_code: dict[str, Coupon] = {c.code: c for c in (coupons or [])}
        self.redeem_calls = 0
        self.save_calls = 0

    async def find_by_code(self, code: str) -> Coupon | None:
        return self._by_code.get(code)

    async def redeem_if_active(self, **_: object) -> bool:
        self.redeem_calls += 1
        return False

    async def save(self, coupon: Coupon) -> Coupon:
        self.save_calls += 1
        return coupon


def _active(code: str = "DOHWA-ABCD-2345") -> Coupon:
    return Coupon.issue(code=code, created_at=datetime(2026, 6, 1, tzinfo=UTC))


async def test_active_coupon_is_valid() -> None:
    repo = FakeCouponRepository([_active()])
    usecase = ValidateCouponUseCase(coupon_repo=repo)

    result = await usecase.execute(code="DOHWA-ABCD-2345")

    assert result.valid is True
    assert repo.redeem_calls == 0 and repo.save_calls == 0, "검증은 읽기 전용"


async def test_unknown_coupon_is_invalid() -> None:
    repo = FakeCouponRepository([])
    usecase = ValidateCouponUseCase(coupon_repo=repo)

    result = await usecase.execute(code="DOHWA-XXXX-XXXX")

    assert result.valid is False


async def test_redeemed_coupon_is_invalid() -> None:
    coupon = _active()
    coupon.status = CouponStatus.REDEEMED
    repo = FakeCouponRepository([coupon])
    usecase = ValidateCouponUseCase(coupon_repo=repo)

    result = await usecase.execute(code="DOHWA-ABCD-2345")

    assert result.valid is False


async def test_code_normalized_before_lookup() -> None:
    repo = FakeCouponRepository([_active(code="DOHWA-ABCD-2345")])
    usecase = ValidateCouponUseCase(coupon_repo=repo)

    result = await usecase.execute(code=" dohwa-abcd-2345 ")

    assert result.valid is True
