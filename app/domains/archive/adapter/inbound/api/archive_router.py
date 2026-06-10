from fastapi import APIRouter, Depends

from app.domains.archive.application.response.archive_response import ArchiveResponse
from app.domains.archive.application.usecase.get_archive_usecase import (
    GetArchiveUseCase,
)
from app.domains.auth.adapter.inbound.api.auth_router import get_current_account_id

router = APIRouter(prefix="/api", tags=["archive"])


# main.py에서 app.dependency_overrides로 교체된다.
def get_archive_usecase() -> GetArchiveUseCase:
    raise NotImplementedError


@router.get("/archive", response_model=ArchiveResponse)
async def get_archive(
    account_id: int = Depends(get_current_account_id),
    usecase: GetArchiveUseCase = Depends(get_archive_usecase),
) -> ArchiveResponse:
    """보관함 — 로그인 계정의 결제 결과 + 깨비 당일 운세."""
    return await usecase.execute(account_id)
