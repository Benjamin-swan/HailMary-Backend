"""이메일 확인 모달 확정 처리 — 확정 후 발송 설계 (2026-06-05 재설계).

구 설계: 결제 확정(webhook) 시 즉시 발송 + 모달에서 수정 시 재발송
  → 오타 주소(남의 주소일 수 있음)로 1통이 먼저 나가고, 수정하면 2통 발송되는 문제.

신 설계:
1. 결과지 합성 완료 시 자동 발송하지 않음 (create_paid_report에서 발송 제거)
2. FE 모달 확정("맞아"든 수정이든) → 본 UseCase 호출 →
   email_confirmed_at 기록 + 결과지 준비됐으면 확정 주소로 발송 + 발송 마킹
3. 결과지가 아직 합성 중이면 확정만 기록 — 스위퍼(EmailDispatchSweeper)가
   준비되는 대로 발송
4. 모달 확정 없이 이탈한 유저 — 스위퍼가 grace(기본 5분) 경과 후 폴백 발송
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


class UpdateEmailAndResendUseCase:
    def __init__(
        self,
        *,
        payment_repo: PaymentRepositoryPort,
        share_lookup: PaidReportShareLookupPort,
        email_resend: EmailResendPort,
    ) -> None:
        self._payment_repo = payment_repo
        self._share_lookup = share_lookup
        self._email_resend = email_resend

    async def execute(self, *, order_id: str, new_email: str) -> None:
        confirmed = await self._payment_repo.confirm_email(
            order_id=order_id,
            email=new_email,
        )
        if confirmed is None:
            raise ValueError("결제 정보를 찾을 수 없습니다.")
        payment, changed = confirmed

        # 이미 발송됐고 주소도 그대로면 재발송 불필요 (스위퍼가 먼저 보낸 케이스).
        if payment.result_email_sent_at is not None and not changed:
            return

        share_code = await self._share_lookup.find_share_code(order_id)
        if share_code is None:
            # PaidReport 합성이 아직 — 확정만 기록. 스위퍼가 준비되는 대로 발송.
            logger.info(
                "[confirm-email] paid report not ready yet for order=%s — confirmed only",
                order_id,
            )
            return

        try:
            await self._email_resend.execute(
                to=payment.customer_email,
                share_code=share_code,
                character=payment.character.value,
                expires_at=payment.expires_at,
            )
            await self._payment_repo.mark_result_email_sent(order_id=order_id)
        except Exception as e:  # noqa: BLE001
            # 발송 실패 시 마킹하지 않음 — 스위퍼가 재시도.
            logger.warning("[confirm-email] send failed for order=%s: %s", order_id, e)
