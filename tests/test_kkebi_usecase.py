"""깨비 일일사주 UseCase 통합테스트 — fake FortuneTeller + fake Repository.

로컬 FortuneTeller 하니스에 의존하지 않고 usecase 조립 로직 전체를 검증한다.
"""
from app.domains.kkebi.application.request.kkebi_fortune_request import KkebiFortuneRequest
from app.domains.kkebi.application.usecase.get_daily_fortune_usecase import (
    GetDailyFortuneUseCase,
)
from app.domains.kkebi.domain.entity.daily_template import DailyTemplate


class FakeFortuneTeller:
    """analyze() 가 사용자 일주(day)를 한글 천간/지지로 반환."""
    def __init__(self, stem: str, branch: str) -> None:
        self._stem = stem
        self._branch = branch

    async def analyze(self, saju_data: dict) -> dict:  # type: ignore[type-arg]
        return {"day": {"stem": self._stem, "branch": self._branch}}


class FakeRepo:
    """find_by_keys 가 어떤 키든 완성 본문을 반환."""
    async def find_by_keys(self, sipseong: str, branch_rel: str) -> DailyTemplate:
        body = {
            "headline": f"{sipseong} 기반 하루를 또렷하게 보는 날.",
            "areas": {
                a: {
                    "summary": f"{a} 한 줄.",
                    "bok": "오늘은 차분한 하루야. 무리 없이 흘러가. 편하게 가도 돼.",
                    "gyeong": "근데 조금 신경 쓸 일도 있어. 살짝 챙겨봐. 크게 흔들리진 않아.",
                    "jo": "깨비가 보기엔 작은 것부터 해봐. 그게 더 든든하잖아. 천천히 가도 돼.",
                }
                for a in ["love", "work", "money", "health", "study"]
            },
            "timeFlow": {
                t: {"comment": "차분한 시간.", "tip": "지금 하는 것에 집중해봐."}
                for t in ["morning", "afternoon", "night"]
            },
        }
        return DailyTemplate(sipseong=sipseong, branch_rel=branch_rel, body=body)

    async def save(self, template: DailyTemplate) -> DailyTemplate:
        return template

    async def list_all(self) -> list[DailyTemplate]:
        return []


async def test_daily_fortune_assembles_full_sajuresult() -> None:
    usecase = GetDailyFortuneUseCase(
        fortuneteller=FakeFortuneTeller("갑", "자"),  # 사용자 일주 甲子
        template_repo=FakeRepo(),
    )
    req = KkebiFortuneRequest(name="수아", birth="1998-03-15", hour=None, gender="F")
    resp = await usecase.execute(req)

    # 프론트 SajuResult 계약 충족
    assert resp.user.name == "수아"
    assert resp.user.gender == "F"
    assert resp.cycle.id
    assert "년" in resp.cycle.displayDate
    assert 70 <= resp.total.score <= 95
    assert resp.total.kkebiMood in {"high", "mid-high", "mid", "low"}
    assert resp.total.summary
    assert set(resp.areas) == {"love", "work", "money", "health", "study"}
    for a in resp.areas.values():
        assert a.blocks.bok and a.blocks.gyeong and a.blocks.jo
        assert 70 <= a.score <= 99
    for ts in (resp.timeFlow.morning, resp.timeFlow.afternoon, resp.timeFlow.night):
        assert ts.comment and ts.tip
    assert resp.lucky.color.hex.startswith("#")
    assert 1 <= resp.lucky.number <= 99
    assert resp.lucky.direction in {"東", "西", "南", "北", "東北", "西北", "東南", "西南"}
    assert resp.lucky.food.name


async def test_gender_mapping() -> None:
    usecase = GetDailyFortuneUseCase(
        fortuneteller=FakeFortuneTeller("갑", "자"),
        template_repo=FakeRepo(),
    )
    for g in ("M", "F", "X"):
        resp = await usecase.execute(
            KkebiFortuneRequest(name="x", birth="2000-01-01", hour=None, gender=g)
        )
        assert resp.user.gender == g
