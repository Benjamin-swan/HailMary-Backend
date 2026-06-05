"""결과지 링크 메일 발송 스위퍼 — 확정-후-발송 설계(2026-06-05)의 폴백 발송자.

발송 대상 (payment_repo.find_email_unsent_done):
  status=DONE & result_email_sent_at IS NULL &
  (email_confirmed_at 있음 OR 결제 후 grace 경과)

커버하는 케이스:
- 모달 확정이 합성 완료보다 빨랐던 건 — 결과지 준비되는 대로 발송
- 모달 확정 없이 이탈한 유저 — grace(기본 5분) 후 결제 시 주소로 폴백 발송
- confirm 시점 발송 실패 건 — 다음 틱에 재시도
- 서버 재시작 — 상태가 전부 DB라 그대로 이어짐 (in-memory 타이머 없음)
"""

from __future__ import annotations

import logging

from app.domains.payment.application.payment_ports import (
    EmailResendPort,
    PaidReportShareLookupPort,
)
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)

logger = logging.getLogger(__name__)

DEFAULT_UNCONFIRMED_GRACE_SECONDS = 300  # 모달 미확정 이탈 유저 폴백 대기 (5분)


class EmailDispatchSweeper:
    def __init__(
        self,
        *,
        payment_repo: PaymentRepositoryPort,
        share_lookup: PaidReportShareLookupPort,
        email_resend: EmailResendPort,
        unconfirmed_grace_seconds: int = DEFAULT_UNCONFIRMED_GRACE_SECONDS,
    ) -> None:
        self._payment_repo = payment_repo
        self._share_lookup = share_lookup
        self._email_resend = email_resend
        self._grace = unconfirmed_grace_seconds

    async def run_once(self) -> int:
        """발송 대기 배치 1회 처리. 발송 성공 건수 반환."""
        pendings = await self._payment_repo.find_email_unsent_done(
            unconfirmed_grace_seconds=self._grace,
        )
        sent = 0
        for payment in pendings:
            share_code = await self._share_lookup.find_share_code(payment.order_id)
            if share_code is None:
                # 결과지 합성 미완 — 다음 틱에 다시.
                continue
            try:
                await self._email_resend.execute(
                    to=payment.customer_email,
                    share_code=share_code,
                    character=payment.character.value,
                    expires_at=payment.expires_at,
                )
                await self._payment_repo.mark_result_email_sent(
                    order_id=payment.order_id
                )
                sent += 1
                logger.info(
                    "[email-sweeper] sent result link order=%s confirmed=%s",
                    payment.order_id,
                    payment.email_confirmed_at is not None,
                )
            except Exception as e:  # noqa: BLE001 — 한 건 실패가 배치를 막지 않게
                logger.warning(
                    "[email-sweeper] send failed order=%s: %s", payment.order_id, e
                )
        return sent
