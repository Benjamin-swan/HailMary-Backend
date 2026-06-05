"""RedeemCouponUseCase 핵심 분기 단위 테스트.

대상:
    1. happy path — amount=0 Payment(DONE) 생성 + 쿠폰 REDEEMED + 합성 백그라운드 스폰
    2. 합성 비대기 — redeem 은 합성 완료를 기다리지 않고 즉시 반환(이 기능의 핵심 보증)
    3. 무효 코드 — 거부, save/합성 스폰 0회
    4. 이미 소진된 코드 — 거부
    5. 원자성/중복 제출 — 두 번째는 거부, 발급 1회만
    6. 세션 만료 — ValueError, 소진·합성 시도 자체 없음
    7. 코드 정규화 — 소문자/공백 입력도 매칭

Mock 전략: unittest.mock 대신 Port 직접 구현 fake.
"""

import asyncio
from collections.abc import Coroutine
from datetime import UTC, datetime
from typing import Any

import pytest

from app.domains.payment.application.usecase.redeem_coupon_usecase import (
    CouponNotRedeemableError,
    RedeemCouponUseCase,
)
from app.domains.payment.domain.entity.coupon import Coupon
from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.port.analytics_port import AnalyticsPort
from app.domains.payment.domain.port.coupon_repository_port import (
    CouponRepositoryPort,
)
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)
from app.domains.payment.domain.value_object.coupon_status import CouponStatus
from app.domains.payment.domain.value_object.payment_status import (
    CharacterCode,
    PaymentStatus,
)

# ── Test fakes ────────────────────────────────────────────────────────────────


class FakeCouponRepository(CouponRepositoryPort):
    """In-memory 쿠폰 저장소. redeem_if_active 가 ACTIVE→REDEEMED 원자 전이를 흉내."""

    def __init__(self, coupons: list[Coupon] | None = None) -> None:
        self._by_code: dict[str, Coupon] = {}
        self.redeem_calls: list[str] = []
        for c in coupons or []:
            self._by_code[c.code] = c

    async def find_by_code(self, code: str) -> Coupon | None:
        return self._by_code.get(code)

    async def redeem_if_active(
        self,
        *,
        code: str,
        user_id: int,
        order_id: str,
        used_at: datetime,
    ) -> bool:
        self.redeem_calls.append(code)
        coupon = self._by_code.get(code)
        if coupon is None or coupon.status != CouponStatus.ACTIVE:
            return False
        coupon.status = CouponStatus.REDEEMED
        coupon.used_at = used_at
        coupon.used_by_user_id = user_id
        coupon.used_order_id = order_id
        return True

    async def save(self, coupon: Coupon) -> Coupon:
        self._by_code[coupon.code] = coupon
        return coupon


class FakePaymentRepository(PaymentRepositoryPort):
    def __init__(self) -> None:
        self._by_order_id: dict[str, Payment] = {}
        self.save_calls: list[Payment] = []

    async def save(self, payment: Payment) -> Payment:
        self.save_calls.append(payment)
        saved = Payment(
            payment_key=payment.payment_key,
            order_id=payment.order_id,
            user_id=payment.user_id,
            character=payment.character,
            amount=payment.amount,
            status=payment.status,
            customer_email=payment.customer_email,
            approved_at=payment.approved_at,
            expires_at=payment.expires_at,
            id=payment.id or len(self._by_order_id) + 1,
        )
        self._by_order_id[payment.order_id] = saved
        return saved

    async def find_by_order_id(self, order_id: str) -> Payment | None:
        return self._by_order_id.get(order_id)

    async def find_by_payment_key(self, payment_key: str) -> Payment | None:
        for p in self._by_order_id.values():
            if p.payment_key == payment_key:
                return p
        return None

    async def update_status(
        self, *, order_id: str, status: PaymentStatus, approved_at: datetime | None = None
    ) -> Payment | None:
        return self._by_order_id.get(order_id)

    async def update_customer_email(
        self, *, order_id: str, new_email: str
    ) -> Payment | None:
        return self._by_order_id.get(order_id)

    async def confirm_email(
        self, *, order_id: str, email: str
    ) -> tuple[Payment, bool] | None:
        p = self._by_order_id.get(order_id)
        if p is None:
            return None
        changed = p.customer_email != email
        return p, changed

    async def mark_result_email_sent(self, *, order_id: str) -> None:
        return None

    async def find_email_unsent_done(
        self, *, unconfirmed_grace_seconds: int, limit: int = 20
    ) -> list[Payment]:
        return []


class FakeUserLookup:
    def __init__(self, mapping: dict[str, int] | None = None) -> None:
        self._mapping = mapping if mapping is not None else {"VALID-TOKEN": 42}

    async def find_user_id_by_session_token(self, token: str) -> int | None:
        return self._mapping.get(token)


class FakeBackgroundComposer:
    """백그라운드 합성 callable fake.

    호출(스폰) 시점에 calls 기록, 실제 코루틴 실행(이벤트 루프 tick 후) 시 ran=True.
    → "스폰됐지만 아직 실행 안 됨"으로 redeem 이 합성을 await 하지 않음을 검증.
    """

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.ran = False

    def __call__(self, **kwargs: Any) -> Coroutine[Any, Any, None]:
        self.calls.append(kwargs)

        async def _run() -> None:
            self.ran = True

        return _run()


class FakeAnalytics(AnalyticsPort):
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def track_payment_completed(self, **kwargs: Any) -> None:
        self.calls.append(kwargs)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _active_coupon(code: str = "DOHWA-ABCD-2345", memo: str = "insta_review") -> Coupon:
    return Coupon.issue(code=code, created_at=datetime(2026, 6, 1, tzinfo=UTC), memo=memo)


def _usecase(
    *,
    coupon_repo: FakeCouponRepository,
    repo: FakePaymentRepository,
    user_lookup: FakeUserLookup | None = None,
    background_composer: FakeBackgroundComposer | None = None,
    analytics: FakeAnalytics | None = None,
) -> RedeemCouponUseCase:
    return RedeemCouponUseCase(
        coupon_repo=coupon_repo,
        repo=repo,
        user_lookup=user_lookup or FakeUserLookup(),
        background_composer=background_composer,
        analytics=analytics,
        user_demographics=None,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


async def test_happy_path_creates_free_payment_and_spawns_compose() -> None:
    coupon = _active_coupon()
    coupon_repo = FakeCouponRepository([coupon])
    repo = FakePaymentRepository()
    composer = FakeBackgroundComposer()
    usecase = _usecase(coupon_repo=coupon_repo, repo=repo, background_composer=composer)

    order_id = await usecase.execute(
        session_token="VALID-TOKEN",
        character=CharacterCode.YEONWOO,
        customer_email="buyer@example.com",
        code="DOHWA-ABCD-2345",
    )

    assert order_id.startswith("coupon_")
    assert len(repo.save_calls) == 1
    saved = repo.save_calls[0]
    assert saved.amount == 0, "무료 쿠폰은 PayApp 우회 — amount 0"
    assert saved.status == PaymentStatus.DONE
    assert coupon.status == CouponStatus.REDEEMED
    assert coupon.used_by_user_id == 42
    assert coupon.used_order_id == order_id

    # 합성은 스폰되었지만 redeem 반환 시점엔 아직 실행 전 (= await 하지 않음)
    assert len(composer.calls) == 1, "합성 백그라운드 스폰 1회"
    assert composer.ran is False, "redeem 은 합성 완료를 기다리지 않는다"
    assert composer.calls[0]["order_id"] == order_id
    assert composer.calls[0]["character"] == "yeonwoo"

    # 이벤트 루프 tick → 백그라운드 task 가 실제로 합성 실행
    await asyncio.sleep(0)
    assert composer.ran is True


async def test_unknown_code_rejected() -> None:
    coupon_repo = FakeCouponRepository([])  # 코드 없음
    repo = FakePaymentRepository()
    composer = FakeBackgroundComposer()
    usecase = _usecase(coupon_repo=coupon_repo, repo=repo, background_composer=composer)

    with pytest.raises(CouponNotRedeemableError):
        await usecase.execute(
            session_token="VALID-TOKEN",
            character=CharacterCode.YEONWOO,
            customer_email="buyer@example.com",
            code="DOHWA-XXXX-XXXX",
        )

    assert repo.save_calls == [], "무효 코드면 결제 생성 금지"
    assert composer.calls == [], "무효 코드면 합성 스폰 금지"


async def test_already_redeemed_code_rejected() -> None:
    coupon = _active_coupon()
    coupon.status = CouponStatus.REDEEMED  # 이미 소진
    coupon_repo = FakeCouponRepository([coupon])
    repo = FakePaymentRepository()
    usecase = _usecase(coupon_repo=coupon_repo, repo=repo)

    with pytest.raises(CouponNotRedeemableError):
        await usecase.execute(
            session_token="VALID-TOKEN",
            character=CharacterCode.YEONWOO,
            customer_email="buyer@example.com",
            code="DOHWA-ABCD-2345",
        )

    assert repo.save_calls == []


async def test_double_submit_redeems_only_once() -> None:
    """동일 코드 두 번 제출 — 두 번째는 거부, 발급은 1회만(원자성)."""
    coupon = _active_coupon()
    coupon_repo = FakeCouponRepository([coupon])
    repo = FakePaymentRepository()
    usecase = _usecase(coupon_repo=coupon_repo, repo=repo)

    first = await usecase.execute(
        session_token="VALID-TOKEN",
        character=CharacterCode.YEONWOO,
        customer_email="buyer@example.com",
        code="DOHWA-ABCD-2345",
    )
    assert first.startswith("coupon_")

    with pytest.raises(CouponNotRedeemableError):
        await usecase.execute(
            session_token="VALID-TOKEN",
            character=CharacterCode.YEONWOO,
            customer_email="buyer@example.com",
            code="DOHWA-ABCD-2345",
        )

    assert len(repo.save_calls) == 1, "원자적 소진 — 결제는 1회만 생성"


async def test_expired_session_does_not_attempt_redeem() -> None:
    coupon = _active_coupon()
    coupon_repo = FakeCouponRepository([coupon])
    repo = FakePaymentRepository()
    composer = FakeBackgroundComposer()
    usecase = _usecase(
        coupon_repo=coupon_repo,
        repo=repo,
        user_lookup=FakeUserLookup({}),  # 토큰 매핑 없음
        background_composer=composer,
    )

    with pytest.raises(ValueError):
        await usecase.execute(
            session_token="EXPIRED",
            character=CharacterCode.YEONWOO,
            customer_email="buyer@example.com",
            code="DOHWA-ABCD-2345",
        )

    assert coupon_repo.redeem_calls == [], "세션 무효면 소진 시도 자체 없음"
    assert coupon.status == CouponStatus.ACTIVE, "쿠폰 보존"
    assert repo.save_calls == []
    assert composer.calls == [], "세션 무효면 합성 스폰 없음"


async def test_code_normalized_before_lookup() -> None:
    """소문자/공백 입력도 저장된 대문자 코드와 매칭된다."""
    coupon = _active_coupon(code="DOHWA-ABCD-2345")
    coupon_repo = FakeCouponRepository([coupon])
    repo = FakePaymentRepository()
    usecase = _usecase(coupon_repo=coupon_repo, repo=repo)

    order_id = await usecase.execute(
        session_token="VALID-TOKEN",
        character=CharacterCode.YEONWOO,
        customer_email="buyer@example.com",
        code="  dohwa-abcd-2345 ",
    )

    assert order_id.startswith("coupon_")
    assert coupon.status == CouponStatus.REDEEMED


async def test_analytics_fired_with_zero_amount() -> None:
    coupon = _active_coupon()
    coupon_repo = FakeCouponRepository([coupon])
    repo = FakePaymentRepository()
    analytics = FakeAnalytics()
    usecase = _usecase(coupon_repo=coupon_repo, repo=repo, analytics=analytics)

    await usecase.execute(
        session_token="VALID-TOKEN",
        character=CharacterCode.YEONWOO,
        customer_email="buyer@example.com",
        code="DOHWA-ABCD-2345",
    )
    await asyncio.sleep(0)  # fire-and-forget 완료 대기

    assert len(analytics.calls) == 1
    assert analytics.calls[0]["amount"] == 0
    assert "customer_email" not in analytics.calls[0], "PII 금지"
