from abc import ABC, abstractmethod
from datetime import datetime

from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.value_object.payment_status import PaymentStatus


class PaymentRepositoryPort(ABC):
    @abstractmethod
    async def save(self, payment: Payment) -> Payment: ...

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> Payment | None: ...

    @abstractmethod
    async def find_by_payment_key(self, payment_key: str) -> Payment | None: ...

    @abstractmethod
    async def update_status(
        self,
        *,
        order_id: str,
        status: PaymentStatus,
        approved_at: datetime | None = None,
    ) -> Payment | None:
        """결제 상태 갱신 (PayApp webhook 처리용). 없으면 None 반환."""
        ...

    @abstractmethod
    async def update_customer_email(
        self,
        *,
        order_id: str,
        new_email: str,
    ) -> Payment | None:
        """결제 완료 후 사용자가 메일 수정 시 호출. 없으면 None 반환."""
        ...

    @abstractmethod
    async def confirm_email(
        self,
        *,
        order_id: str,
        email: str,
    ) -> tuple[Payment, bool] | None:
        """이메일 확인 모달 확정 — 주소가 다르면 갱신 + email_confirmed_at 기록.

        Returns:
            (payment, changed) — changed=True면 주소가 실제로 바뀜. 없으면 None.
        """
        ...

    @abstractmethod
    async def mark_result_email_sent(self, *, order_id: str) -> None:
        """결과지 링크 메일 발송 완료 마킹 (result_email_sent_at=now)."""
        ...

    @abstractmethod
    async def find_email_unsent_done(
        self,
        *,
        unconfirmed_grace_seconds: int,
        limit: int = 20,
    ) -> list[Payment]:
        """발송 대기 결제 조회 (스위퍼용) — status=DONE & 미발송 &
        (확정됨 OR 결제 후 grace 경과). 확정 없이 이탈한 유저 폴백 발송 대상."""
        ...
