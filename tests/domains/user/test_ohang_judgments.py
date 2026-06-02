"""오행 강약 per-element 판정(classify_ohang_strength) 테스트.

QA 5건(테갑남01·테을여04·테병남05·테병여06·테무여10)에서 반복 보고된 버그:
무료 결과는 여러 오행을 '과다'로 보여주는데, 유료 P-0는 '제일 강한 1개만 과다,
나머지는 전부 낮음'으로 표기됨. 원인은 유료가 argmax/argmin 단일값만 썼기 때문.

성공 기준: 유료 P-0 막대 판정이 무료 결과(_build_wuxing)와 **동일**해야 한다.
이 테스트가 두 코드 경로의 임계값/라운딩 drift를 막는 SSOT 가드다.
"""

from __future__ import annotations

from app.domains.user.application.saju_view_mapper import _build_wuxing
from app.domains.user.domain.service.saju_data_extractor import (
    classify_ohang_strength,
)


def test_multiple_elements_can_be_excess() -> None:
    """다중 과다 — 버그의 핵심: 강한 오행이 2개 이상이면 모두 '과다'여야 한다."""
    # 목 3, 화 3 → 각 37.5% (≥32 과다), 금/수 12.5% 적정, 토 0% 결핍.
    wc = {"목": 3, "화": 3, "토": 0, "금": 1, "수": 1}
    judged = classify_ohang_strength(wc)
    assert judged["목"] == "과다"
    assert judged["화"] == "과다"  # 단일-argmax 버그면 여기서 '적정/발달'로 떨어짐
    assert judged["토"] == "결핍"
    assert judged["금"] == "적정"
    assert judged["수"] == "적정"


def test_strong_non_max_element_is_not_understated() -> None:
    """최댓값이 아니어도 비율이 높으면 '발달/과다'로 잡혀야 한다.

    구 FE 휴리스틱(value<40 → '낮음')과 구 BE(max 1개만 과다) 조합의 회귀 방지.
    """
    # 수 5(50%) 과다, 목 3(30%) 발달 — 목은 max가 아니지만 '낮음'이면 안 됨.
    wc = {"목": 3, "화": 1, "토": 1, "금": 0, "수": 5}
    judged = classify_ohang_strength(wc)
    assert judged["수"] == "과다"
    assert judged["목"] == "발달"  # 30% → 발달 (낮음/적정 아님)


def test_all_zero_counts_all_deficient() -> None:
    judged = classify_ohang_strength({})
    assert set(judged.values()) == {"결핍"}


def test_parity_with_free_result_build_wuxing() -> None:
    """무료 플로(_build_wuxing)와 라벨이 완전히 동일한지 — drift 가드(SSOT)."""
    samples = [
        {"목": 1, "화": 0, "토": 1, "금": 1, "수": 5},   # 임수 과다(테스트 fixture)
        {"목": 3, "화": 3, "토": 0, "금": 1, "수": 1},   # 다중 과다
        {"목": 2, "화": 2, "토": 2, "금": 1, "수": 1},   # 경계값 주변
        {"목": 1, "화": 1, "토": 1, "금": 1, "수": 1},   # 균등(전부 적정)
        {"목": 8, "화": 0, "토": 0, "금": 0, "수": 0},   # 단일 100%
        {},                                              # 빈 입력
    ]
    for wc in samples:
        assert classify_ohang_strength(wc) == _build_wuxing(wc)["judgments"], wc
