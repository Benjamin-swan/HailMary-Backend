from pydantic import BaseModel, Field


class ValidateCouponRequest(BaseModel):
    """쿠폰 "적용" 버튼 — 코드 유효성 확인 요청."""

    code: str = Field(min_length=1, max_length=64)
