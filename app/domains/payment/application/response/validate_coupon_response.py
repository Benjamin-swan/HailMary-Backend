from pydantic import BaseModel


class ValidateCouponResponse(BaseModel):
    valid: bool
    message: str
