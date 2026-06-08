from pydantic import BaseModel

from app.domains.auth.domain.value_object.provider import Provider


class SocialLoginRequest(BaseModel):
    provider: Provider
    code: str
    # FE가 인가 요청에 사용한 redirect_uri 그대로 — 제공자가 교환 시 일치 검증.
    redirect_uri: str
