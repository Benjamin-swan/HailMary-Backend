"""도윤 P-9 데이터 풀 — 六 연애 변수 최적화 가이드.

원본 도윤_final.html data-page-idx=9 구조 정합.
- 6-1: 오행 보완 방법 × 3 (색채/공간/행동) — 오행 5종 매트릭스
- 6-2: 리스크 카드 × 3 (즉시/단기/중기) — 일간 무관 공통
- 6-3: 매력 최적화 — 일간별 (현재/목표 + 부스트)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OhangMethodCard:
    label: str        # "보완 방법 1 · 효과 +9%"
    keyword: str      # "색채 노출 — 초록 계열"
    desc: str


@dataclass(frozen=True)
class RiskCard:
    label: str        # "즉시 · 위험도 81%"
    tone: str         # "warn" / "warn" / "amber"
    keyword: str      # "미정리 관계 변수"
    desc: str


@dataclass(frozen=True)
class DoyoonP9IlganData:
    """일간별 P-9 — 매력 최적화."""
    current_score: int       # 85
    target_score: int        # 92
    gap_per_action: str      # "1.3%"
    overall_boost_pct: str   # "21%"
    optimize_bubble: str
    sd_optimize_asset: str   # "dy_06"


# ── 6-1 오행 보완 매트릭스 (5 오행) ───────────────────────────────


_OHANG_METHODS_TEMPLATE = {
    "목": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="초록 계열 포인트",
                        desc="{ohang_lack} 기운을 색으로 채워주는 방법. 옷이나 소품에서 노출을 조금씩 늘려보세요."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="동쪽을 가까이",
                        desc="동쪽이 {ohang_lack}과 잘 어울리는 방향이에요. 책상·침대 머리 방향을 그쪽으로 두세요."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="아침 산책 30분",
                        desc="하루 리듬을 차분히 잡아줘요. 식물이나 자연광을 함께 누리면 더 좋아요."),
    ),
    "화": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="붉은 계열 포인트",
                        desc="{ohang_lack} 기운을 색으로 채워주는 방법. 액세서리나 소품으로 가볍게 더해보세요."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="남쪽을 가까이",
                        desc="남쪽이 {ohang_lack}과 잘 어울리는 방향이에요. 조명이나 창문 방향을 그쪽으로 살려보세요."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="햇볕 산책 20분",
                        desc="햇빛을 쬐면 {ohang_lack} 기운이 한결 살아나요."),
    ),
    "토": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="황토·베이지 포인트",
                        desc="{ohang_lack} 기운을 색으로 채워주는 방법. 인테리어나 옷차림에 자연스럽게 녹여보세요."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="가운데 자리를 챙기기",
                        desc="공간의 중심이 {ohang_lack}과 잘 어울려요. 자리를 정돈하면 더 차분해져요."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="흙·도예 가까이",
                        desc="손으로 감각을 채워주는 방법. 화분이나 정원을 가까이 두면 더 좋아요."),
    ),
    "금": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="흰색·은색 포인트",
                        desc="{ohang_lack} 기운을 색으로 채워주는 방법. 메탈 소재 액세서리를 곁들여보세요."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="서쪽을 가까이",
                        desc="서쪽이 {ohang_lack}과 잘 어울리는 방향이에요. 일출·일몰을 보는 자리를 만들어보세요."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="정리·운동 루틴",
                        desc="규칙적인 흐름을 채워줘요. 시간표를 또렷하게 잡으면 더 잘 잡혀요."),
    ),
    "수": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="검정·짙은 청색 포인트",
                        desc="{ohang_lack} 기운을 색으로 채워주는 방법. 옷차림에서 비율을 조금 늘려보세요."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="북쪽을 가까이",
                        desc="북쪽이 {ohang_lack}과 잘 어울리는 방향이에요. 물이 보이는 공간을 살리면 좋아요."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="수영·반신욕",
                        desc="물과 가까이 지내며 채워주는 방법. 주 2회 이상이면 흐름이 한결 잘 잡혀요."),
    ),
}


def get_ohang_methods(ohang_lack: str) -> tuple[OhangMethodCard, OhangMethodCard, OhangMethodCard]:
    """ohang_lack ('목'/'화'/'토'/'금'/'수') → 보완 방법 카드 3개 (desc에 ohang_lack 치환)."""
    tmpl = _OHANG_METHODS_TEMPLATE.get(ohang_lack) or _OHANG_METHODS_TEMPLATE["목"]
    return tuple(  # type: ignore[return-value]
        OhangMethodCard(
            label=c.label,
            keyword=c.keyword,
            desc=c.desc.replace("{ohang_lack}", ohang_lack),
        )
        for c in tmpl
    )


# ── 6-2 리스크 카드 × 3 (일간 무관 공통) ──────────────────────────


RISK_CARDS: tuple[RiskCard, RiskCard, RiskCard] = (
    RiskCard(
        label="즉시 · 위험도 81%",
        tone="warn",
        keyword="정리되지 않은 관계",
        desc="새 인연이 들어오는 길을 가장 크게 막아요. 하루 안에 한 번 정리해 보세요.",
    ),
    RiskCard(
        label="단기 · 위험도 64%",
        tone="warn",
        keyword="감정적인 순간의 결정",
        desc="욱하는 순간에 말이 앞서기 쉬워요. 하루 두고 보는 습관이 도움돼요.",
    ),
    RiskCard(
        label="중기 · 위험도 47%",
        tone="amber",
        keyword="반복되는 일상",
        desc="새로운 사람을 만날 자리가 좁아요. 한 달에 한 번은 낯선 환경에 가보세요.",
    ),
)

# 리스크 사실값 (공통)
IMMEDIATE_IMPACT_PCT: str = "36%"
# COMBINED_EFFECT_*(단순합산 192 → 1.4배 → 130) 상수는 QA F-056(무의미한 위험도 합산) 지적으로 제거.


# ── 6-3 매력 최적화 (일간 10셀) ───────────────────────────────────


DOYOON_P9_DATA: dict[str, DoyoonP9IlganData] = {
    "갑목": DoyoonP9IlganData(
        current_score=83, target_score=90, gap_per_action="1.2%", overall_boost_pct="19%",
        optimize_bubble="분석은 다 끝났어요. 이제 {USER_NAME}님 결정만 남았어요.",
        sd_optimize_asset="dy_06",
    ),
    "을목": DoyoonP9IlganData(
        current_score=82, target_score=89, gap_per_action="1.2%", overall_boost_pct="20%",
        optimize_bubble="가벼운 신호 하나로 흐름이 움직여요. {USER_NAME}님이 먼저예요.",
        sd_optimize_asset="dy_06",
    ),
    "병화": DoyoonP9IlganData(
        current_score=86, target_score=93, gap_per_action="1.4%", overall_boost_pct="22%",
        optimize_bubble="발산 매력이 강점이에요. {USER_NAME}님이 한 번 빨리 표현하시면 됩니다.",
        sd_optimize_asset="dy_06",
    ),
    "정화": DoyoonP9IlganData(
        current_score=84, target_score=91, gap_per_action="1.3%", overall_boost_pct="21%",
        optimize_bubble="깊은 표현 한 번이 흐름을 바꿔요. {USER_NAME}님 차례입니다.",
        sd_optimize_asset="dy_06",
    ),
    "무토": DoyoonP9IlganData(
        current_score=85, target_score=91, gap_per_action="1.2%", overall_boost_pct="19%",
        optimize_bubble="안정 케이스라 작은 변화도 누적 효과 커요. {USER_NAME}님이 시작이에요.",
        sd_optimize_asset="dy_06",
    ),
    "기토": DoyoonP9IlganData(
        current_score=83, target_score=90, gap_per_action="1.2%", overall_boost_pct="20%",
        optimize_bubble="배려가 강점이에요. {USER_NAME}님의 작은 신호가 결정적입니다.",
        sd_optimize_asset="dy_06",
    ),
    "경금": DoyoonP9IlganData(
        current_score=86, target_score=92, gap_per_action="1.3%", overall_boost_pct="20%",
        optimize_bubble="명확성이 무기예요. {USER_NAME}님이 직접적으로 전달하시면 됩니다.",
        sd_optimize_asset="dy_06",
    ),
    "신금": DoyoonP9IlganData(
        current_score=84, target_score=91, gap_per_action="1.3%", overall_boost_pct="21%",
        optimize_bubble="섬세한 신호 하나가 흐름을 바꿔요. {USER_NAME}님 차례입니다.",
        sd_optimize_asset="dy_06",
    ),
    "임수": DoyoonP9IlganData(
        current_score=85, target_score=92, gap_per_action="1.3%", overall_boost_pct="21%",
        optimize_bubble="분석은 다 끝났어요. 이제 공은 {USER_NAME}님한테 있어요.",
        sd_optimize_asset="dy_06",
    ),
    "계수": DoyoonP9IlganData(
        current_score=83, target_score=91, gap_per_action="1.4%", overall_boost_pct="23%",
        optimize_bubble="잠재 매력이 가장 큰 케이스예요. {USER_NAME}님이 시작만 하시면 돼요.",
        sd_optimize_asset="dy_06",
    ),
}


VALID_DOYOON_P9_ILGAN: frozenset[str] = frozenset(DOYOON_P9_DATA.keys())


# 6-1 공통 사실값
OHANG_BOOST_PCT: str = "23%"
OHANG_RESPONSE_MULTIPLIER: str = "1.6배"
OHANG_MAX_BOOST_PCT: str = "28%"
