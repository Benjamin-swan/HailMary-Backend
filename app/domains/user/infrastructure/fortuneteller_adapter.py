from typing import Any

from app.infrastructure.external.fortuneteller.client import FortuneTellerClient


class FortuneTellerAdapter:
    """FortuneTellerPort 구현체. FortuneTellerClient를 Domain Port 인터페이스로 감싼다."""

    def __init__(self, client: FortuneTellerClient) -> None:
        self._client = client

    async def analyze(self, saju_data: dict[str, Any]) -> dict[str, Any]:
        return await self._client.analyze(saju_data)
