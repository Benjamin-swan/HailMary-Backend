"""깨비 일일사주 Redis 캐시 통합 테스트 (HM-BE-67).

fakeredis 기반 — 실 Redis 컨테이너 없이 캐시 hit/miss/TTL/PII 분리/회귀 검증.

5 케이스:
1. pillars 캐시 hit → FortuneTeller 호출 회피
2. result 캐시 hit → template_repo 호출 회피 (전체 합성 skip)
3. 캐시 키는 hour/gender 무관 (같은 birth → 같은 슬롯 공유)
4. TTL 정확 (pillars 30일, result 25h)
5. PII(개인정보) cache value에 없음 (BE CLAUDE.md 룰 정합)

추가: cache=None 회귀 검증 (기존 test_kkebi_usecase.py 무변경 동작 확인용).
"""
from __future__ import annotations

from typing import Any

from app.domains.kkebi.application.request.kkebi_fortune_request import (
    KkebiFortuneRequest,
)
from app.domains.kkebi.application.usecase.get_daily_fortune_usecase import (
    GetDailyFortuneUseCase,
)
from app.domains.kkebi.domain.entity.daily_template import DailyTemplate
from app.infrastructure.cache.cache_key_builder import (
    kkebi_pillars_key,
    kkebi_result_key,
)
from app.infrastructure.cache.redis_client import RedisCache


class CountingFortuneTeller:
    """analyze 호출 횟수를 카운트해서 캐시 우회 여부 검증용."""

    def __init__(self, stem: str = "갑", branch: str = "자") -> None:
        self._stem = stem
        self._branch = branch
        self.call_count = 0

    async def analyze(self, saju_data: dict[str, Any]) -> dict[str, Any]:
        self.call_count += 1
        return {"day": {"stem": self._stem, "branch": self._branch}}


class CountingRepo:
    """find_by_keys 호출 횟수 카운트. body는 고정."""

    def __init__(self) -> None:
        self.call_count = 0

    async def find_by_keys(self, sipseong: str, branch_rel: str) -> DailyTemplate:
        self.call_count += 1
        body = {
            "headline": f"{sipseong}×{branch_rel} 하루를 또렷하게 보는 날.",
            "areas": {
                a: {
                    "summary": f"{a} 한 줄.",
                    "bok": "오늘은 차분한 하루야.",
                    "gyeong": "근데 신경 쓸 일도 있어.",
                    "jo": "작은 것부터 해봐.",
                }
                for a in ["love", "work", "money", "health", "study"]
            },
            "timeFlow": {
                t: {"comment": "차분한 시간.", "tip": "지금에 집중해봐."}
                for t in ["morning", "afternoon", "night"]
            },
        }
        return DailyTemplate(sipseong=sipseong, branch_rel=branch_rel, body=body)

    async def save(self, template: DailyTemplate) -> DailyTemplate:
        return template

    async def list_all(self) -> list[DailyTemplate]:
        return []


# ─── 케이스 1. pillars 캐시 hit → FortuneTeller skip ──────────────────────────

async def test_pillars_cache_hit_skips_fortuneteller(
    fake_redis_cache: RedisCache,
) -> None:
    ft = CountingFortuneTeller()
    repo = CountingRepo()
    usecase = GetDailyFortuneUseCase(
        fortuneteller=ft, template_repo=repo, cache=fake_redis_cache
    )
    req = KkebiFortuneRequest(name="수아", birth="1996-05-29", hour=11, gender="F")

    await usecase.execute(req)
    await usecase.execute(req)
    await usecase.execute(req)

    # 첫 호출만 FortuneTeller 도달, 나머지 두 번은 pillars 캐시 hit
    assert ft.call_count == 1


# ─── 케이스 2. result 캐시 hit → template_repo skip ────────────────────────────

async def test_result_cache_hit_short_circuits_template_lookup(
    fake_redis_cache: RedisCache,
) -> None:
    ft = CountingFortuneTeller()
    repo = CountingRepo()
    usecase = GetDailyFortuneUseCase(
        fortuneteller=ft, template_repo=repo, cache=fake_redis_cache
    )
    req = KkebiFortuneRequest(name="수아", birth="1996-05-29", hour=11, gender="F")

    await usecase.execute(req)
    await usecase.execute(req)

    # 첫 호출 — full 합성 (FortuneTeller 1, template_repo 1)
    # 둘째 호출 — result 캐시 hit → template_repo 호출 0회 추가
    assert repo.call_count == 1


# ─── 케이스 3. hour/gender 무관 — 같은 birth → 같은 캐시 슬롯 ─────────────────

async def test_cache_key_independent_of_gender_and_hour(
    fake_redis_cache: RedisCache,
) -> None:
    ft = CountingFortuneTeller()
    repo = CountingRepo()
    usecase = GetDailyFortuneUseCase(
        fortuneteller=ft, template_repo=repo, cache=fake_redis_cache
    )

    # 같은 birth, 다른 hour/gender
    await usecase.execute(
        KkebiFortuneRequest(name="A", birth="1996-05-29", hour=11, gender="F")
    )
    await usecase.execute(
        KkebiFortuneRequest(name="B", birth="1996-05-29", hour=None, gender="M")
    )
    await usecase.execute(
        KkebiFortuneRequest(name="C", birth="1996-05-29", hour=23, gender="X")
    )

    # 일주는 birth만 영향 → pillars 캐시는 첫 호출만 set, 나머지는 hit
    assert ft.call_count == 1
    # result 캐시도 같은 stem/branch + 같은 date → 첫 호출만 합성, 나머지는 hit
    assert repo.call_count == 1


# ─── 케이스 4. TTL 정확 ──────────────────────────────────────────────────────

async def test_ttl_set_correctly(fake_redis_cache: RedisCache) -> None:
    ft = CountingFortuneTeller()
    repo = CountingRepo()
    pillars_ttl = 60 * 60 * 24 * 30
    result_ttl = 60 * 60 * 25
    usecase = GetDailyFortuneUseCase(
        fortuneteller=ft,
        template_repo=repo,
        cache=fake_redis_cache,
        pillars_ttl_seconds=pillars_ttl,
        result_ttl_seconds=result_ttl,
    )
    req = KkebiFortuneRequest(name="수아", birth="1996-05-29", hour=11, gender="F")
    await usecase.execute(req)

    # pillars: birth만 키. fakeredis ttl()로 검증.
    pillars_remaining = await fake_redis_cache._redis.ttl(kkebi_pillars_key("1996-05-29"))
    assert pillars_ttl - 5 <= pillars_remaining <= pillars_ttl

    # result: stem/branch/date. fake FortuneTeller가 '갑/자' 반환.
    from datetime import datetime, timedelta, timezone
    today_iso = datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    result_remaining = await fake_redis_cache._redis.ttl(
        kkebi_result_key("갑", "자", today_iso)
    )
    assert result_ttl - 5 <= result_remaining <= result_ttl


# ─── 케이스 5. PII 분리 — cache value에 name/birth/gender 없음 ────────────────

async def test_pii_not_in_cache_value(fake_redis_cache: RedisCache) -> None:
    ft = CountingFortuneTeller()
    repo = CountingRepo()
    usecase = GetDailyFortuneUseCase(
        fortuneteller=ft, template_repo=repo, cache=fake_redis_cache
    )
    req = KkebiFortuneRequest(
        name="개인정보_절대유출X",
        birth="1996-05-29",
        hour=11,
        gender="F",
    )
    await usecase.execute(req)

    # result 캐시 값 직접 조회 → cycle/total/timeFlow/areas/lucky만 있어야 함
    from datetime import datetime, timedelta, timezone
    today_iso = datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    cached = await fake_redis_cache.get_json(
        kkebi_result_key("갑", "자", today_iso)
    )
    assert cached is not None
    assert "user" not in cached
    # 직접 키 검사
    assert set(cached.keys()) == {"cycle", "total", "timeFlow", "areas", "lucky"}
    # 본문에 name/birth/gender literal이 등장하지 않는지(2차 안전 검증)
    import json
    serialized = json.dumps(cached, ensure_ascii=False)
    assert "개인정보_절대유출X" not in serialized
    assert "1996-05-29" not in serialized
    # gender 한 글자(F/M/X)는 흔한 문자라 검사 제외

    # pillars 캐시값도 검증 — stem/branch만
    pillars_cached = await fake_redis_cache.get_json(kkebi_pillars_key("1996-05-29"))
    assert pillars_cached == {"stem": "갑", "branch": "자"}


# ─── 회귀 검증 — cache=None일 때 기존 동작 유지 ──────────────────────────────

async def test_no_cache_regression_passes() -> None:
    """cache=None 기본값일 때 기존 흐름 그대로 — test_kkebi_usecase.py 회귀 가드."""
    ft = CountingFortuneTeller()
    repo = CountingRepo()
    usecase = GetDailyFortuneUseCase(fortuneteller=ft, template_repo=repo)
    req = KkebiFortuneRequest(name="x", birth="2000-01-01", hour=None, gender="X")

    await usecase.execute(req)
    await usecase.execute(req)

    # 캐시 없으니 매 호출마다 FortuneTeller + template_repo 둘 다 도달
    assert ft.call_count == 2
    assert repo.call_count == 2


# ─── 동등성 락다운 (★ 핵심) — 캐시 전후 응답 의미 변동 0 ──────────────────────

async def test_cache_response_equivalence_locks_down_no_drift(
    fake_redis_cache: RedisCache,
) -> None:
    """캐시 도입으로 응답이 미세하게 달라지지 않는지 영구 회귀 가드.

    A: cache=None (캐시 도입 전 동작)
    B: 캐시 있고 cold (full 합성 + cache set)
    C: 캐시 있고 warm (cache hit)

    A.model_dump() == B.model_dump() == C.model_dump() 가 영구 보장되어야 함.
    이 테스트가 깨지는 순간 → 캐시가 응답 의미를 변경했다는 신호 → 즉시 조사.
    """
    req = KkebiFortuneRequest(
        name="동등성검증", birth="2000-06-15", hour=14, gender="F"
    )

    # A: 캐시 미사용
    usecase_a = GetDailyFortuneUseCase(
        fortuneteller=CountingFortuneTeller("을", "묘"),
        template_repo=CountingRepo(),
    )
    resp_a = await usecase_a.execute(req)

    # B: 캐시 cold (1차 호출 — full 합성 + cache set 동시)
    ft_b = CountingFortuneTeller("을", "묘")
    repo_b = CountingRepo()
    usecase_b = GetDailyFortuneUseCase(
        fortuneteller=ft_b,
        template_repo=repo_b,
        cache=fake_redis_cache,
    )
    resp_b = await usecase_b.execute(req)

    # C: 캐시 warm (같은 fake_redis_cache 재사용 → 2차 호출은 hit)
    ft_c = CountingFortuneTeller("을", "묘")
    repo_c = CountingRepo()
    usecase_c = GetDailyFortuneUseCase(
        fortuneteller=ft_c,
        template_repo=repo_c,
        cache=fake_redis_cache,
    )
    resp_c = await usecase_c.execute(req)

    # 응답 의미 = model_dump 동등 (필드별 dict 비교)
    dump_a = resp_a.model_dump()
    dump_b = resp_b.model_dump()
    dump_c = resp_c.model_dump()

    assert dump_a == dump_b, "캐시 미사용 vs cold 합성 불일치 — 캐시 set 로직이 응답 변경"
    assert dump_b == dump_c, "cold vs warm 불일치 — 캐시 hit 재조립 로직 결함"

    # 부수 검증: warm 케이스는 외부 호출 전혀 안 함
    assert ft_c.call_count == 0, "캐시 hit인데 FortuneTeller 호출 발생"
    assert repo_c.call_count == 0, "캐시 hit인데 template_repo 호출 발생"
