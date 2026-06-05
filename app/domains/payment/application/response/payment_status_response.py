from pydantic import BaseModel, ConfigDict, Field


class PaymentStatusResponse(BaseModel):
    """FE polling 응답. PayApp 결제완료(webhook 수신) 여부 확인용."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: str = Field(alias="orderId")
    # PaymentStatus enum 그대로 (READY/DONE/CANCELED/ABORTED/WAITING_FOR_DEPOSIT/PARTIAL_CANCELED)
    status: str
    character: str
    # 2026-06-05: 카드사 인증 복귀 시 storage 유실로 FE가 이메일을 잃는 케이스 →
    # 이메일 확인 모달 프리필용으로 서버가 내려줌 (빈칸이면 수정→이중발송 유발돼서)
    customer_email: str = Field(alias="customerEmail", default="")
