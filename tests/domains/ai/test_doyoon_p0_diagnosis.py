"""도윤 P-0 ai_intro AI prompt builder + validate + usecase fallback 단위 테스트."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p0_diagnosis_usecase import (
    GenerateP0DiagnosisUseCase,
)
from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p0_diagnosis_prompt import (
    build_p0_diagnosis_prompt,
    validate_p0_diagnosis,
)
from app.domains.ai.domain.templates.doyoon_p0_intro import get_doyoon_p0_facts

# ── facts 추출 ────────────────────────────────────────────────────


def test_get_facts_html_dummy() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    assert f["user_name"] == "홍길동"
    assert f["ilgan_full"] == "임수"
    assert f["ilgan_hanja"] == "壬水"
    assert f["excess_ohang_hanja"] == "水"
    assert f["lack_ohang_hanja"] == "土"
    # 수치(백분위·접촉률) 키는 2026-06-05 폐기 — facts에 더 이상 없음
    assert "excess_percentile" not in f
    assert "lack_percentile" not in f
    assert "contact_rate_drop" not in f
    # rule_text는 합성된 4단락
    assert "홍길동님" in f["rule_text"]
    assert f["rule_text"].count("\n\n") == 3


def test_get_facts_user_name_required() -> None:
    with pytest.raises(ValueError, match="user_name"):
        get_doyoon_p0_facts(
            user_name="", ilgan="임수", ohang_excess="수", ohang_lack="토"
        )


def test_get_facts_unknown_ilgan() -> None:
    with pytest.raises(KeyError):
        get_doyoon_p0_facts(
            user_name="홍길동", ilgan="모름", ohang_excess="수", ohang_lack="토"
        )


# ── prompt builder ───────────────────────────────────────────────


def test_build_prompt_substitutes_facts() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    system, user = build_p0_diagnosis_prompt(f)
    # system: 페르소나 + 사실값 박힘 (오행 한자, 수치는 폐기)
    assert "한도윤" in system
    assert "홍길동" in system
    assert "水" in system
    assert "土" in system
    # user: 사실값 + rule_text 박힘
    assert "user_name: 홍길동" in user
    assert "ilgan_hanja: 壬水" in user
    assert "壬水" in user
    assert f["rule_text"] in user


def test_build_prompt_missing_key_raises() -> None:
    incomplete = {"user_name": "홍길동"}  # 나머지 누락
    with pytest.raises(KeyError, match="missing facts keys"):
        build_p0_diagnosis_prompt(incomplete)


# ── validate ────────────────────────────────────────────────────


def _valid_text(facts: dict[str, str]) -> str:
    """검증 통과하는 가상 AI 출력. _MIN_LENGTH=180 이상 보장. 수치 미포함(2026-06-05)."""
    return (
        f"{facts['user_name']}님, 입력 데이터 정리가 모두 끝났습니다. "
        "분석 준비도 같이 마쳤어요.\n\n"
        f"일간은 {facts['ilgan_full']}({facts['ilgan_hanja']}) — 강점 분포가 또렷하게 드러나요. "
        "첫인상에서 속도가 붙는 흐름이 보이는 유형입니다. 초반 관계 형성에 유리한 편이에요.\n\n"
        f"다만 {facts['excess_ohang_hanja']} 기운이 뚜렷하게 과다하고, "
        f"{facts['lack_ohang_hanja']} 기운은 눈에 띄게 부족한 것으로 나타나요. "
        "이 두 변수가 연애 영역에 직접 영향을 줍니다. "
        "한쪽이 넘치고 한쪽이 받쳐주지 못하면 흐름이 흔들리는 지점이 생겨요.\n\n"
        "다음 장에서 변수별 영향과 우선순위를 분석해드릴게요."
    )


def test_validate_passes_with_facts_preserved() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    text = _valid_text(f)
    ok, reason = validate_p0_diagnosis(text, f)
    assert ok, f"unexpected fail: {reason}"


def test_validate_fails_user_name_missing() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    text = _valid_text(f).replace("홍길동", "OOO")
    ok, reason = validate_p0_diagnosis(text, f)
    assert not ok
    assert "user_name" in reason


def test_validate_fails_ohang_hanja_mutated() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    # AI가 부족 오행 한자 土를 누락 (土는 임수/水에 안 겹쳐 격리 검증됨)
    text = _valid_text(f).replace("土", "흙")
    ok, reason = validate_p0_diagnosis(text, f)
    assert not ok
    assert "lack_ohang_hanja" in reason


def test_validate_fails_length_too_short() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    ok, reason = validate_p0_diagnosis("짧음", f)
    assert not ok
    assert "length" in reason


def test_validate_fails_paragraph_structure() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    # 모든 fact 포함하되 단락 구분 제거 (길이는 유지하려 빈칸 2개로 치환)
    text = _valid_text(f).replace("\n\n", "  ")
    ok, reason = validate_p0_diagnosis(text, f)
    assert not ok
    assert "paragraph structure" in reason


# ── usecase: AI 성공 / 실패 / 검증실패 fallback ────────────────────


class _FakeAIClient(AIClientPort):
    """테스트용 stub. .response_text 또는 .raise_exc 설정."""

    def __init__(
        self,
        *,
        response_text: str | None = None,
        raise_exc: Exception | None = None,
    ) -> None:
        self.response_text = response_text
        self.raise_exc = raise_exc
        self.calls: list[dict[str, object]] = []

    async def generate_chapter(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.85,
        model: str | None = None,
    ) -> str:
        self.calls.append({
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        })
        if self.raise_exc is not None:
            raise self.raise_exc
        assert self.response_text is not None
        return self.response_text


@pytest.mark.asyncio
async def test_usecase_returns_ai_text_on_success() -> None:
    f = get_doyoon_p0_facts(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    ai_text = _valid_text(f)
    fake = _FakeAIClient(response_text=ai_text)
    usecase = GenerateP0DiagnosisUseCase(ai_client=fake)
    out = await usecase.execute(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    assert out == ai_text
    # P-10과 동일 sonnet 4.6 모델로 호출 (톤 일관성)
    assert len(fake.calls) == 1
    assert fake.calls[0]["model"] == "claude-sonnet-4-6"


@pytest.mark.asyncio
async def test_usecase_falls_back_on_ai_error() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    usecase = GenerateP0DiagnosisUseCase(ai_client=fake)
    out = await usecase.execute(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    # 룰 fallback — 4단락 + 사실값 포함 (수치 없이 질적 표현)
    assert "홍길동님" in out
    assert "壬水" in out
    assert "水가 넘치면" in out
    assert out.count("\n\n") == 3


@pytest.mark.asyncio
async def test_usecase_falls_back_on_validation_fail() -> None:
    # AI가 사실값 누락한 응답 반환 → 검증 실패 → 룰 fallback
    fake = _FakeAIClient(
        response_text="홍길동님, 분석이 끝났어요. " * 30  # 사실값 포함 X
    )
    usecase = GenerateP0DiagnosisUseCase(ai_client=fake)
    out = await usecase.execute(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    # AI 텍스트 아니고 룰 fallback (단락 구조 + 사실값 정확)
    assert out.count("\n\n") == 3
    assert "壬水" in out
    assert "水가 넘치면" in out
