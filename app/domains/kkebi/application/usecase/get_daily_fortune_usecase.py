"""깨비 일일사주 조회 UseCase.

흐름:
  1. FortuneTeller analyze → 사용자 일주(일간·일지). 일일운세는 일주만 쓰므로 time="unknown".
  2. 오늘(KST) 일진 60갑자 계산.
  3. 십성 × 지지관계 산출.
  4. 매칭 템플릿(본문) 조회.
  5. 점수/무드/lucky 룰 계산.
  6. 프론트 SajuResult 형태로 조립.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domains.kkebi.application.request.kkebi_fortune_request import KkebiFortuneRequest
from app.domains.kkebi.application.response.daily_fortune_response import (
    AreaView,
    BirthView,
    BlocksView,
    ColorView,
    CycleView,
    DailyFortuneResponse,
    FoodView,
    LuckyView,
    TimeFlowView,
    TimeSlotView,
    TotalView,
    UserView,
)
from app.domains.kkebi.domain.port.daily_template_repository_port import (
    DailyTemplateRepositoryPort,
)
from app.domains.kkebi.domain.port.fortuneteller_port import FortuneTellerPort
from app.domains.kkebi.domain.service.ganzhi_calendar import (
    cycle_id,
    day_ganzhi,
)
from app.domains.kkebi.domain.service.kkebi_mood import to_kkebi_mood
from app.domains.kkebi.domain.service.lucky_rules import lucky_for
from app.domains.kkebi.domain.service.saju_rules import (
    derive_branch_relation,
    derive_sipseong,
)
from app.domains.kkebi.domain.service.score_rules import (
    AREAS,
    score_area,
    score_time,
    score_total,
)

_KST = timezone(timedelta(hours=9))
_MONTH_DAY_KO = "{y}년 {m}월 {d}일"


class GetDailyFortuneUseCase:
    def __init__(
        self,
        fortuneteller: FortuneTellerPort,
        template_repo: DailyTemplateRepositoryPort,
    ) -> None:
        self._ft = fortuneteller
        self._repo = template_repo

    async def execute(self, request: KkebiFortuneRequest) -> DailyFortuneResponse:
        # 1. 사용자 일주
        saju_data = {
            "birth": request.birth,
            "time": "unknown",   # 일주는 날짜만으로 결정 — 시각 불필요(야자시 엣지 회피)
            "calendar": "solar",
            "gender": request.gender_value(),
        }
        ft = await self._ft.analyze(saju_data)
        day = ft.get("day") or {}
        user_stem = str(day.get("stem", ""))
        user_branch = str(day.get("branch", ""))
        if not user_stem or not user_branch:
            raise ValueError("FortuneTeller 응답에 일주(day) 정보가 없습니다")

        # 2. 오늘 일진 (KST)
        today = datetime.now(_KST).date()
        today_stem, today_branch = day_ganzhi(today)

        # 3. 십성 × 지지관계
        sipseong = derive_sipseong(user_stem, today_stem)
        branch_rel = derive_branch_relation(user_branch, today_branch)

        # 4. 템플릿 본문
        template = await self._repo.find_by_keys(sipseong, branch_rel)
        if template is None:
            raise ValueError(f"템플릿 없음: {sipseong}×{branch_rel}")
        body = template.body

        # 5. 룰 계산
        total = score_total(sipseong, branch_rel)
        lucky = lucky_for(today_stem, today_branch, user_stem, user_branch)

        # 6. 조립
        time_flow = TimeFlowView(
            morning=TimeSlotView(
                score=score_time(sipseong, "morning"),
                comment=body["timeFlow"]["morning"]["comment"],
                tip=body["timeFlow"]["morning"]["tip"],
            ),
            afternoon=TimeSlotView(
                score=score_time(sipseong, "afternoon"),
                comment=body["timeFlow"]["afternoon"]["comment"],
                tip=body["timeFlow"]["afternoon"]["tip"],
            ),
            night=TimeSlotView(
                score=score_time(sipseong, "night"),
                comment=body["timeFlow"]["night"]["comment"],
                tip=body["timeFlow"]["night"]["tip"],
            ),
        )
        areas = {
            a: AreaView(
                score=score_area(sipseong, a),
                summary=body["areas"][a]["summary"],
                blocks=BlocksView(
                    bok=body["areas"][a]["bok"],
                    gyeong=body["areas"][a]["gyeong"],
                    jo=body["areas"][a]["jo"],
                ),
            )
            for a in AREAS
        }

        return DailyFortuneResponse(
            user=UserView(
                name=request.name,
                birth=BirthView(date=request.birth, hour=request.hour),
                gender=request.gender,
            ),
            cycle=CycleView(
                id=cycle_id(today),
                displayDate=_MONTH_DAY_KO.format(y=today.year, m=today.month, d=today.day),
            ),
            total=TotalView(
                score=total,
                summary=body["headline"],
                kkebiMood=to_kkebi_mood(total),
            ),
            timeFlow=time_flow,
            areas=areas,
            lucky=LuckyView(
                color=ColorView(hex=lucky["color"]["hex"], name=lucky["color"]["name"]),
                number=lucky["number"],
                direction=lucky["direction"],
                food=FoodView(name=lucky["food"]["name"]),
            ),
        )
