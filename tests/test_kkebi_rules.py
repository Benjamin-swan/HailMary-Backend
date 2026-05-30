"""깨비 도메인 룰 단위테스트 — 외부 의존성 없이 순수 검증."""
from datetime import date

from app.domains.kkebi.domain.service.ganzhi_calendar import cycle_id, day_ganzhi, ganzhi_index
from app.domains.kkebi.domain.service.kkebi_mood import to_kkebi_mood
from app.domains.kkebi.domain.service.lucky_rules import lucky_for
from app.domains.kkebi.domain.service.saju_rules import (
    derive_branch_relation,
    derive_sipseong,
)
from app.domains.kkebi.domain.service.score_rules import (
    AREAS,
    SCORE_FLOOR,
    TIME_SLOTS,
    score_area,
    score_time,
    score_total,
)


# --- 60갑자 (알려진 기준일 교차검증) ---
def test_ganzhi_known_anchors():
    assert day_ganzhi(date(2000, 1, 1)) == ("戊", "午")   # 2000-01-01 = 戊午
    assert day_ganzhi(date(2000, 1, 7)) == ("甲", "子")   # 2000-01-07 = 甲子 (시작)

def test_ganzhi_cycle_60():
    # 60일 뒤 같은 갑자
    assert ganzhi_index(date(2000, 1, 7)) == ganzhi_index(date(2000, 3, 7))
    assert day_ganzhi(date(2000, 1, 7)) == day_ganzhi(date(2000, 3, 7))

def test_cycle_id_format():
    assert cycle_id(date(2026, 5, 22)) == "20260522"


# --- 십성/지지관계 (한글·한자 동등) ---
def test_sipseong_hangul_hanja_equal():
    assert derive_sipseong("갑", "무") == derive_sipseong("甲", "戊")
    assert derive_branch_relation("자", "진") == derive_branch_relation("子", "辰")

def test_sipseong_self():
    assert derive_sipseong("甲", "甲") == "비견"

def test_branch_self():
    assert derive_branch_relation("子", "子") == "동주"


_SIPSEONGS = ["비견","겁재","식신","상관","편재","정재","편관","정관","편인","정인"]
_RELS = ["합","충","형","파","해","동주","보통"]


# --- 점수 floor 70 / ceil 99 ---
def test_score_floor_and_ceil():
    from app.domains.kkebi.domain.service.score_rules import SCORE_CEIL
    for ss in _SIPSEONGS:
        for br in _RELS:
            assert SCORE_FLOOR <= score_total(ss, br) <= SCORE_CEIL
        for a in AREAS:
            assert SCORE_FLOOR <= score_area(ss, a) <= SCORE_CEIL
        for t in TIME_SLOTS:
            assert SCORE_FLOOR <= score_time(ss, t) <= SCORE_CEIL


# --- 영역 점수 평탄화 방지 (십성마다 5영역이 서로 다른 값) ---
def test_area_scores_not_flat():
    for ss in _SIPSEONGS:
        vals = [score_area(ss, a) for a in AREAS]
        assert len(set(vals)) >= 4, f"{ss} 영역점수 평평: {vals}"


# --- 점수 분포 (고객경험: 70대 20% / 80대 50% / 90대 30%, ±10%p 허용) ---
def test_score_distribution():
    vals = [score_total(ss, br) for ss in _SIPSEONGS for br in _RELS]
    n = len(vals)
    b70 = sum(1 for v in vals if 70 <= v < 80) / n
    b80 = sum(1 for v in vals if 80 <= v < 90) / n
    b90 = sum(1 for v in vals if 90 <= v <= 99) / n
    assert 0.10 <= b70 <= 0.30, f"70대 비율 {b70:.0%}"
    assert 0.40 <= b80 <= 0.60, f"80대 비율 {b80:.0%}"
    assert 0.20 <= b90 <= 0.40, f"90대 비율 {b90:.0%}"


# --- kkebiMood 4단계 (90/80/70 임계) ---
def test_kkebi_mood_bands():
    assert to_kkebi_mood(95) == "high"
    assert to_kkebi_mood(90) == "high"
    assert to_kkebi_mood(89) == "mid-high"
    assert to_kkebi_mood(80) == "mid-high"
    assert to_kkebi_mood(79) == "mid"
    assert to_kkebi_mood(70) == "mid"
    assert to_kkebi_mood(60) == "low"


# --- lucky (오늘 일진 × 사용자 일주 해시) ---
def test_lucky_structure():
    lk = lucky_for("癸", "卯", "甲", "子")
    assert set(lk) == {"color", "number", "direction", "food"}
    assert lk["color"]["hex"].startswith("#")
    assert 1 <= lk["number"] <= 99
    assert lk["direction"] in {"東", "西", "南", "北", "東北", "西北", "東南", "西南"}
    assert lk["food"]["name"]


def test_lucky_deterministic_and_varies():
    # 같은 입력 → 항상 같음 (결정론적)
    a = lucky_for("癸", "卯", "甲", "子")
    b = lucky_for("癸", "卯", "甲", "子")
    assert a == b
    # 같은 날, 다른 사람 → 결과 달라짐 (적어도 한 요소)
    other = lucky_for("癸", "卯", "丙", "寅")
    assert (a["color"], a["number"], a["direction"], a["food"]) != (
        other["color"], other["number"], other["direction"], other["food"]
    )
    # 같은 사람, 다른 날 → 달라짐
    nextday = lucky_for("甲", "辰", "甲", "子")
    assert (a["color"], a["number"], a["direction"]) != (
        nextday["color"], nextday["number"], nextday["direction"]
    )
