from pydantic import BaseModel

from app.domains.auth.application.response.account_profile_response import (
    AccountProfileResponse,
)


class SocialLoginResponse(BaseModel):
    access_token: str
    is_new_account: bool
    profile: AccountProfileResponse
