from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PaidArchiveItem(BaseModel):
    # 만료(30일) 건은 usecase에서 제외 → 여기 담기는 건 모두 열람 가능한 활성 결과지.
    character: str  # "yeonwoo" | "doyoon" — 상품명 표기는 FE가 매핑
    orderId: str
    shareCode: str | None  # None이면 결과지 미합성 → FE에서 '다시 보기' 비활성
    approvedAt: datetime
    expiresAt: datetime


class KkebiArchiveItem(BaseModel):
    cycleId: str
    summary: str | None


class ArchiveResponse(BaseModel):
    paid: list[PaidArchiveItem]
    kkebi: KkebiArchiveItem | None
