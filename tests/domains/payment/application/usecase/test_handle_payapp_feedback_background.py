"""HandlePayAppFeedbackUseCase 결제완료 후속처리 — 유료리포트 합성 백그라운드 분리 (HM-BE-83).

기존엔 webhook 핸들러가 `paid_report_creator.execute`(P0~P4 Claude 합성)를 **inline await** 해
요청 트랜잭션 커밋이 합성 끝까지 지연됐다 → DONE 이 늦게 보여 ① 이메일 팝업/결과 로딩(이탈방지
몰입 콘텐츠)이 마스킹할 새 없이 합성이 먼저 끝나고 ② 응답 지연으로 checkretry 재시도→중복 합성.
쿠폰 경로와 동일한 background_composer 로 분리해 응답/커밋을 합성과 떼어낸다.
"""

import asyncio
from collections.abc import Coroutine
from datetime import UTC, datetime, timedelta
from typing import Any

from app.domains.payment.application.usecase.handle_payapp_feedback_usecase import (
    HandlePayAppFeedbackUseCase,
)
from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.value_object.payment_status import (
    CharacterCode,
    PaymentStatus,
)

LINKKEY = "lk-test"
LINKVAL = "lv-test"
AMOUNT = 7900


class FakeRepo:
    def __init__(self, payment: Payment) -> None:
        self._payment = payment
        self.update_calls: list[PaymentStatus] = []

    async def find_by_order_id(self, order_id: str) -> Payment | None:
        return self._payment if order_id == self._payment.order_id else None

    async def update_status(
        self, *, order_id: str, status: PaymentStatus, approved_at: datetime | None = None
    ) -> Payment | None:
        self.update_calls.append(status)
        p = self._payment
        updated = Payment(
            payment_key=p.payment_key,
            order_id=p.order_id,
            user_id=p.user_id,
            character=p.character,
            amount=p.amount,
            status=status,
            customer_email=p.customer_email,
            approved_at=approved_at if approved_at is not None else p.approved_at,
            expires_at=p.expires_at,
            id=p.id,
        )
        self._payment = updated
        return updated


class FakeBackgroundComposer:
    """백그라운드 합성 callable fake — 스폰 시점 calls 기록, 코루틴 실제 실행 시 ran=True."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.ran = False

    def __call__(self, **kwargs: Any) -> Coroutine[Any, Any, None]:
        self.calls.append(kwargs)

        async def _run() -> None:
            self.ran = True

        return _run()


class FakeCreator:
    """inline 합성 경로 — background_composer 있으면 호출되면 안 됨."""

    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, **kwargs: Any) -> None:
        self.calls += 1


def _payment(*, status: PaymentStatus = PaymentStatus.READY) -> Payment:
    return Payment(
        payment_key="pk-1",
        order_id="order_1",
        user_id=42,
        character=CharacterCode.YEONWOO,
        amount=AMOUNT,
        status=status,
        customer_email="buyer@example.com",
        approved_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=30),
        id=1,
    )


def _done_form() -> dict[str, str]:
    return {
        "linkkey": LINKKEY,
        "linkval": LINKVAL,
        "var1": "order_1",
        "mul_no": "12345",
        "pay_state": "4",  # → DONE
        "price": str(AMOUNT),
        "pay_date": "2026-06-08 01:28:56",
        "pay_type": "1",
    }


def _usecase(
    *,
    repo: FakeRepo,
    background_composer: FakeBackgroundComposer | None = None,
    paid_report_creator: FakeCreator | None = None,
) -> HandlePayAppFeedbackUseCase:
    return HandlePayAppFeedbackUseCase(
        repo=repo,  # type: ignore[arg-type]
        expected_linkkey=LINKKEY,
        expected_linkval=LINKVAL,
        background_composer=background_composer,
        paid_report_creator=paid_report_creator,
    )


async def test_done_spawns_background_compose_not_inline() -> None:
    repo = FakeRepo(_payment())
    composer = FakeBackgroundComposer()
    creator = FakeCreator()
    usecase = _usecase(repo=repo, background_composer=composer, paid_report_creator=creator)

    result = await usecase.execute(_done_form())

    assert result.ok is True
    assert PaymentStatus.DONE in repo.update_calls
    # 합성: 백그라운드 스폰 1회, inline creator 미호출(=응답/커밋이 합성을 안 기다림)
    assert len(composer.calls) == 1, "합성 백그라운드 스폰 1회"
    assert creator.calls == 0, "background_composer 있으면 inline 합성 안 함"
    assert composer.ran is False, "webhook 응답이 합성 완료를 기다리지 않는다"
    assert composer.calls[0]["order_id"] == "order_1"
    assert composer.calls[0]["character"] == "yeonwoo"
    # 이벤트 루프 tick → 백그라운드 task 가 실제로 합성 실행
    await asyncio.sleep(0)
    assert composer.ran is True


async def test_duplicate_done_skips_compose() -> None:
    """이미 DONE 이면 멱등성 skip — 합성 재스폰 없음(중복 합성/중복 과금 방지)."""
    repo = FakeRepo(_payment(status=PaymentStatus.DONE))
    composer = FakeBackgroundComposer()
    usecase = _usecase(repo=repo, background_composer=composer)

    result = await usecase.execute(_done_form())

    assert result.reason == "duplicate_skipped"
    assert composer.calls == [], "중복 webhook 은 합성 재스폰 안 함"


async def test_inline_fallback_when_no_composer() -> None:
    """composer 미주입(테스트/구버전 구성) — 기존대로 inline 합성 fallback."""
    repo = FakeRepo(_payment())
    creator = FakeCreator()
    usecase = _usecase(repo=repo, background_composer=None, paid_report_creator=creator)

    await usecase.execute(_done_form())

    assert creator.calls == 1, "composer 없으면 inline fallback 으로 합성"
