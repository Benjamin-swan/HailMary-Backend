from typing import Any, Protocol


class FortuneTellerPort(Protocol):
    async def analyze(self, saju_data: dict[str, Any]) -> dict[str, Any]: ...
