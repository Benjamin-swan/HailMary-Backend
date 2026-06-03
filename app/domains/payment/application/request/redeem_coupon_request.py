from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.payment.domain.value_object.payment_status import CharacterCode


class RedeemCouponRequest(BaseModel):
    """쿠폰 "무료로 받기" 제출 요청. DevBypassRequest + code.

    prod 노출 — 환경 가드 없음, 유효 쿠폰 코드가 가드 역할.
    """

    model_config = ConfigDict(populate_by_name=True)

    session_token: str = Field(alias="sessionToken", min_length=1)
    character: CharacterCode
    customer_email: EmailStr = Field(alias="customerEmail")
    code: str = Field(min_length=1, max_length=64)
