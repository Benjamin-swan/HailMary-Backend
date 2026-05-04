"""FortuneTeller 응답 dict + 분석 서비스 결과를 묶어 FreeResultResponse 로 변환.

영업비밀 차단 + 프론트 expected shape으로 변환:
  - saju_view_mapper.to_view 에서 pillars/wuxing/yongSin/dayMaster를 프론트 모양으로 산출
  - gyeokGuk, jiJangGan, branchRelations, wolRyeong, specialMarks, dayMasterStrength.score
    /analysis, yongSin.reasoning 등 영업비밀은 출력에 포함되지 않음 (mapper가 emit하지 않음)
"""

from __future__ import annotations

from typing import Any

from app.domains.user.application.response.free_result_response import (
    BlockingView,
    CharmView,
    FreeResultResponse,
    MonthlyRomanceFlowView,
    SpouseAvoidView,
    SpouseMatchView,
)
from app.domains.user.application.saju_view_mapper import to_view


def build_free_result_response(
    *,
    session_token: str,
    saju_data: dict[str, Any],
    charm: dict[str, Any],
    blocking: dict[str, Any],
    spouse_avoid: dict[str, Any],
    spouse_match: dict[str, Any],
    monthly_romance_flow: dict[str, Any],
) -> FreeResultResponse:
    return FreeResultResponse(
        sessionToken=session_token,
        sajuData=to_view(saju_data),
        charm=CharmView.model_validate(charm),
        blocking=BlockingView.model_validate(blocking),
        spouseAvoid=SpouseAvoidView.model_validate(spouse_avoid),
        spouseMatch=SpouseMatchView.model_validate(spouse_match),
        monthlyRomanceFlow=MonthlyRomanceFlowView.model_validate(monthly_romance_flow),
    )
