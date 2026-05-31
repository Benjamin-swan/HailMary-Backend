"""깨비 일일사주 조회 UseCase.

흐름:
  1. FortuneTeller analyze → 사용자 일주(일간·일지). 일일운세는 일주만 쓰므로 time="unknown".
  2. 오늘(KST) 일진 60갑자 계산.
  3. 십성 × 지지관계 산출.
  4. 매칭 템플릿(본문) 조회.
  5. 점수/무드/lucky 룰 계산.
  6. 프론트 SajuResult 형태로 조립.

캐시 (HM-BE-67):
  - pillars 캐시(birth → stem/branch, TTL 30일) → FortuneTeller 호출 회피
  - result 캐시(stem+branch+date → composed, TTL 25h) → 전체 합성 회피
  - 개인정보(user.name/birth/gender)는 cache value에 절대 저장 X — request에서 매번 덮어쓰기
  - Redis 다운 시 graceful fallback (RedisCache 내부 try/except → None) → BE 정상 응답
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

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
from app.infrastructure.cache.cache_key_builder import (
    kkebi_pillars_key,
    kkebi_result_key,
)
from app.infrastructure.cache.redis_client import RedisCache

_KST = timezone(timedelta(hours=9))
_MONTH_DAY_KO = "{y}년 {m}월 {d}일"
# 기본 TTL — main.py에서 settings로 오버라이드. 캐시 비활성 시 무관.
_DEFAULT_PILLARS_TTL = 60 * 60 * 24 * 30   # 30일
_DEFAULT_RESULT_TTL = 60 * 60 * 25          # 25시간


class GetDailyFortuneUseCase:
    def __init__(
        self,
        fortuneteller: FortuneTellerPort,
        template_repo: DailyTemplateRepositoryPort,
        cache: RedisCache | None = None,
        pillars_ttl_seconds: int = _DEFAULT_PILLARS_TTL,
        result_ttl_seconds: int = _DEFAULT_RESULT_TTL,
    ) -> None:
        self._ft = fortuneteller
        self._repo = template_repo
        self._cache = cache
        self._pillars_ttl = pillars_ttl_seconds
        self._result_ttl = result_ttl_seconds

    async def execute(self, request: KkebiFortuneRequest) -> DailyFortuneResponse:
        # 1. 사용자 일주 — pillars 캐시 우선
        user_stem, user_branch = await self._resolve_pillars(request)

        # 2. 오늘 일진 (KST)
        today = datetime.now(_KST).date()
        today_iso = today.isoformat()

        # 3. result 캐시 우선 — hit 시 user 필드만 request에서 덮어쓰기
        if self._cache is not None:
            result_cached = await self._cache.get_json(
                kkebi_result_key(user_stem, user_branch, today_iso)
            )
            if result_cached is not None:
                return self._assemble_from_cache(request, result_cached)

        # 4. cache miss → 합성 (기존 흐름)
        today_stem, today_branch = day_ganzhi(today)
        sipseong = derive_sipseong(user_stem, today_stem)
        branch_rel = derive_branch_relation(user_branch, today_branch)

        template = await self._repo.find_by_keys(sipseong, branch_rel)
        if template is None:
            raise ValueError(f"템플릿 없음: {sipseong}×{branch_rel}")
        body = template.body

        total = score_total(sipseong, branch_rel)
        lucky = lucky_for(today_stem, today_branch, user_stem, user_branch)

        # 5. PII-free 응답 컴포넌트 빌드 (캐시 + 반환 양쪽에 재사용)
        cycle_view = CycleView(
            id=cycle_id(today),
            displayDate=_MONTH_DAY_KO.format(y=today.year, m=today.month, d=today.day),
        )
        total_view = TotalView(
            score=total,
            summary=body["headline"],
            kkebiMood=to_kkebi_mood(total),
        )
        time_flow_view = TimeFlowView(
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
        areas_view = {
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
        lucky_view = LuckyView(
            color=ColorView(hex=lucky["color"]["hex"], name=lucky["color"]["name"]),
            number=lucky["number"],
            direction=lucky["direction"],
            food=FoodView(name=lucky["food"]["name"]),
        )

        # 6. result 캐시 set (PII 제외, user 필드는 캐시 안 함)
        if self._cache is not None:
            await self._cache.set_json(
                kkebi_result_key(user_stem, user_branch, today_iso),
                {
                    "cycle": cycle_view.model_dump(),
                    "total": total_view.model_dump(),
                    "timeFlow": time_flow_view.model_dump(),
                    "areas": {a: areas_view[a].model_dump() for a in AREAS},
                    "lucky": lucky_view.model_dump(),
                },
                ttl_seconds=self._result_ttl,
            )

        # 7. 최종 응답 — user 필드는 request에서 직접 조립 (캐시 비경유)
        return DailyFortuneResponse(
            user=self._build_user_view(request),
            cycle=cycle_view,
            total=total_view,
            timeFlow=time_flow_view,
            areas=areas_view,
            lucky=lucky_view,
        )

    # ─── 내부 헬퍼 ─────────────────────────────────────────────────────────────

    async def _resolve_pillars(self, request: KkebiFortuneRequest) -> tuple[str, str]:
        """일주(stem/branch) 추출. pillars 캐시 hit 시 FortuneTeller 호출 skip."""
        if self._cache is not None:
            cached = await self._cache.get_json(kkebi_pillars_key(request.birth))
            if isinstance(cached, dict):
                stem = str(cached.get("stem", ""))
                branch = str(cached.get("branch", ""))
                if stem and branch:
                    return stem, branch

        # cache miss → FortuneTeller 호출
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

        # pillars 캐시 set (birth만 key, 시/성별 무관)
        if self._cache is not None:
            await self._cache.set_json(
                kkebi_pillars_key(request.birth),
                {"stem": user_stem, "branch": user_branch},
                ttl_seconds=self._pillars_ttl,
            )

        return user_stem, user_branch

    def _build_user_view(self, request: KkebiFortuneRequest) -> UserView:
        return UserView(
            name=request.name,
            birth=BirthView(date=request.birth, hour=request.hour),
            gender=request.gender,
        )

    def _assemble_from_cache(
        self,
        request: KkebiFortuneRequest,
        cached: dict[str, Any],
    ) -> DailyFortuneResponse:
        """result 캐시 hit 시 user 필드만 request에서 덮어쓰기 (PII 분리)."""
        return DailyFortuneResponse(
            user=self._build_user_view(request),
            cycle=CycleView(**cached["cycle"]),
            total=TotalView(**cached["total"]),
            timeFlow=TimeFlowView(**cached["timeFlow"]),
            areas={a: AreaView(**cached["areas"][a]) for a in cached["areas"]},
            lucky=LuckyView(**cached["lucky"]),
        )
