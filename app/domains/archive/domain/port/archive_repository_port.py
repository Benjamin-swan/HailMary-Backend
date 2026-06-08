from typing import Protocol

from app.domains.archive.domain.value_object.archive_rows import (
    KkebiArchiveRow,
    PaidArchiveRow,
)


class ArchiveRepositoryPort(Protocol):
    async def list_paid(self, account_id: int) -> list[PaidArchiveRow]:
        """계정 귀속 결제(DONE) + 결과지 share_code 조인, 최신순."""
        ...

    async def find_kkebi_today(
        self, account_id: int, cycle_id: str
    ) -> KkebiArchiveRow | None:
        """오늘 저장된 깨비 운세 요약 (없으면 None)."""
        ...
