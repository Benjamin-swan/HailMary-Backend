from typing import Any, Protocol


class FortuneTellerPort(Protocol):
    """FortuneTeller 호출 포트. user 도메인의 FortuneTellerAdapter가 구조적으로 충족."""

    async def analyze(self, saju_data: dict[str, Any]) -> dict[str, Any]:
        ...
