from typing import Any

from pydantic import BaseModel


class FreeResultResponse(BaseModel):
    saju_request_id: int
    saju_data: dict[str, Any]  # FortuneTeller 응답 그대로
