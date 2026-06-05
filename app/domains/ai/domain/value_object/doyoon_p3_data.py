"""도윤 P-3 데이터 풀 — 원본 도윤_final.html data-page-idx=3 구조 정합.

오행 5셀 (BlockadeOhangData) + 일간 10셀 (DoyoonP3IlganData) 매트릭스.
- 2-1 구조적 원인: 오행 dimension (ohang_excess 기반)
- 2-2 반복 패턴: 일간 dimension (3 패턴 × 10 일간)
- 2-2-1 변수 통제: 일간 dimension (2 strategies × 10 일간)

임수 일간 + 수 과다 셀은 원본 더미 그대로, 나머지는 도윤 톤 압축.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlockadeOhangData:
    """오행 과다 구조적 원인 — 큰 card-warn 1 매핑."""
    ohang_hanja: str               # "水"
    blockade_pct: str              # "상위 15%"
    blockade_multiplier: str       # 비수치 강도 표현 (예: "평소보다 크게") — DTO 호환 위해 필드명 유지
    blockage_rate_drop: str        # "36%"
    recovery_after_clearing_pct: str  # "24%"


@dataclass(frozen=True)
class PatternEntry:
    """반복 실수 패턴 — card-warn × 3 매핑."""
    keyword: str                   # "처음부터 너무 깊이"
    pct: str                       # "81%"
    multiplier: str                # 비수치 강도 표현 — DTO 호환 위해 필드명 유지 (프로즈 미사용)
    desc: str


@dataclass(frozen=True)
class ControlStrategy:
    """바로 해볼 수 있는 방법 — card-good × 2 매핑."""
    keyword: str                   # "마음 표현 속도 조절하기"
    desc: str
    effect_pct: str                # "47%"


@dataclass(frozen=True)
class DoyoonP3IlganData:
    """일간별 P-3 데이터 (패턴 + 통제 + 안정성 + 버블 3종)."""
    patterns: tuple[PatternEntry, PatternEntry, PatternEntry]
    strategies: tuple[ControlStrategy, ControlStrategy]
    stability_boost_pct: str       # "41%"
    blockade_bubble: str
    pattern_bubble: str
    strategy_bubble: str


# 도윤_final.html 원본 SD asset (2-2-1 spotlight 고정)
P3_SD_ASSET: str = "dy_10"


# ────────────────────────────────────────────────────────────────
# 오행 5셀 — BlockadeOhangData
# ────────────────────────────────────────────────────────────────

# 임수+수 과다 케이스는 원본 더미. 나머지 4 오행은 정량 정책 §2 범위로 작성.
BLOCKADE_BY_OHANG: dict[str, BlockadeOhangData] = {
    "수": BlockadeOhangData(
        ohang_hanja="水",
        blockade_pct="상위 15%",
        blockade_multiplier="평소보다 크게",
        blockage_rate_drop="36%",
        recovery_after_clearing_pct="24%",
    ),
    "목": BlockadeOhangData(
        ohang_hanja="木",
        blockade_pct="상위 13%",
        blockade_multiplier="한결 더",
        blockage_rate_drop="28%",
        recovery_after_clearing_pct="22%",
    ),
    "화": BlockadeOhangData(
        ohang_hanja="火",
        blockade_pct="상위 12%",
        blockade_multiplier="두드러지게",
        blockage_rate_drop="32%",
        recovery_after_clearing_pct="26%",
    ),
    "토": BlockadeOhangData(
        ohang_hanja="土",
        blockade_pct="상위 17%",
        blockade_multiplier="제법 두드러지게",
        blockage_rate_drop="24%",
        recovery_after_clearing_pct="20%",
    ),
    "금": BlockadeOhangData(
        ohang_hanja="金",
        blockade_pct="상위 14%",
        blockade_multiplier="훨씬 크게",
        blockage_rate_drop="30%",
        recovery_after_clearing_pct="23%",
    ),
}


# ────────────────────────────────────────────────────────────────
# 일간 10셀 — DoyoonP3IlganData
# ────────────────────────────────────────────────────────────────

DOYOON_P3_DATA: dict[str, DoyoonP3IlganData] = {
    # ── 임수 (원본 더미) ───────────────────────────────────────
    "임수": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="처음부터 너무 깊이", pct="81%", multiplier="두드러지게",
                         desc="첫 한 달 동안 마음을 한꺼번에 쏟아붓는 편이에요."),
            PatternEntry(keyword="중간에 표현이 줄어듦", pct="67%", multiplier="47%",
                         desc="마음은 그대로인데 말로 드러내는 게 눈에 띄게 줄어들어요."),
            PatternEntry(keyword="쌓였다가 한 번에 터짐", pct="54%", multiplier="두드러지게",
                         desc="참아둔 감정이 어느 순간 한꺼번에 쏟아져 나오곤 해요."),
        ),
        strategies=(
            ControlStrategy(keyword="마음 표현 속도 조절하기",
                            desc="한 주에 표현하는 정도를 미리 정해두기. 이 한 가지만 지켜도 한꺼번에 터지는 일이 눈에 띄게 줄어요.",
                            effect_pct="47%"),
            ControlStrategy(keyword="감정 하루 묵혔다 말하기",
                            desc="마음이 일렁인 직후 말고 하루 지난 뒤에 표현해보기. 충동적으로 쏟아내는 일이 한결 줄어들어요.",
                            effect_pct="38%"),
        ),
        stability_boost_pct="41%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="사람은 바뀌어도 패턴은 잘 안 바뀌어요. 그래서 한 번 짚어두는 게 의미가 있어요.",
        strategy_bubble="지금 이 글을 읽고 계신다는 것 자체가 이미 다음 연애가 달라진다는 신호예요.",
    ),
    # ── 갑목 ───────────────────────────────────────────────────
    "갑목": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="앞만 보고 밀어붙임", pct="76%", multiplier="두드러지게",
                         desc="한번 마음먹으면 뒤돌아보거나 다시 살피는 일이 드문 편이에요."),
            PatternEntry(keyword="맞춰가기를 피함", pct="62%", multiplier="43%",
                         desc="서로 조율하자는 말이 나오면 반응이 눈에 띄게 줄어들어요."),
            PatternEntry(keyword="한번 어긋나면 돌아섬", pct="58%", multiplier="두드러지게",
                         desc="신뢰가 깨지면 다시 다가가기보다 그대로 등을 돌리곤 해요."),
        ),
        strategies=(
            ControlStrategy(keyword="결정 전 잠깐 멈추기",
                            desc="결정 직전에 잠깐만 숨을 고르고 돌아봐도 뒤따르는 다툼이 한결 줄어들어요.",
                            effect_pct="38%"),
            ControlStrategy(keyword="상대 제안 한 번 받아주기",
                            desc="상대가 내미는 의견 하나를 일부러라도 받아주면 관계가 한결 안정적으로 흘러가요.",
                            effect_pct="32%"),
        ),
        stability_boost_pct="36%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="단호한 게 강점이지만, 단호함만으로는 관계가 쌓이지 않아요.",
        strategy_bubble="잠깐 멈추는 게 결정을 흔드는 게 아니에요. 더 나은 선택을 하게 돕는 거예요.",
    ),
    # ── 을목 ───────────────────────────────────────────────────
    "을목": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="상대에게 너무 맞춤", pct="78%", multiplier="두드러지게",
                         desc="상대에게 맞추다 보면 정작 본인 마음을 잘 못 드러내요."),
            PatternEntry(keyword="내 마음을 잘 안 비침", pct="71%", multiplier="38%",
                         desc="원하는 걸 분명히 말하는 일이 다른 분들보다 적은 편이에요."),
            PatternEntry(keyword="다 받아주다 지침", pct="56%", multiplier="두드러지게",
                         desc="갈등을 혼자 끌어안다가 어느 순간 한계에 다다르곤 해요."),
        ),
        strategies=(
            ControlStrategy(keyword="내 마음 한 줄 꺼내기",
                            desc="한 주에 한 번이라도 원하는 걸 또렷하게 말해보기. 관계 안에서 본인 자리가 다시 보여요.",
                            effect_pct="35%"),
            ControlStrategy(keyword="받아줄 선 정해두기",
                            desc="어디까지 받아줄지 미리 정해두기. 혼자 쌓아두다 터지는 일이 한결 줄어들어요.",
                            effect_pct="31%"),
        ),
        stability_boost_pct="33%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="유연하게 맞춰주는 게 강점인데, 맞추기만 하면 본인이 사라져요.",
        strategy_bubble="내 마음 한 줄이 매주 들어가야 관계 안에서 본인이 보여요.",
    ),
    # ── 병화 ───────────────────────────────────────────────────
    "병화": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="처음부터 화끈하게", pct="83%", multiplier="두드러지게",
                         desc="첫 만남부터 마음을 강하게 드러내는 편이에요."),
            PatternEntry(keyword="반응이 약하면 식음", pct="69%", multiplier="42%",
                         desc="기대만큼 반응이 안 오면 마음이 빠르게 닫혀버려요."),
            PatternEntry(keyword="기분 따라 온도 차", pct="51%", multiplier="두드러지게",
                         desc="뜨거웠다 차가워지는 변화가 자주 오가는 편이에요."),
        ),
        strategies=(
            ControlStrategy(keyword="천천히 데우기",
                            desc="첫 몇 주는 마음의 온도를 조금 낮춰 다가가면 관계가 더 오래 이어져요.",
                            effect_pct="39%"),
            ControlStrategy(keyword="상대 속도 살피며 맞추기",
                            desc="상대가 따라올 수 있는 속도인지 먼저 살핀 뒤 다가가면 마음이 닫히는 일이 줄어요.",
                            effect_pct="34%"),
        ),
        stability_boost_pct="38%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="빛을 비추기 전에, 그 빛을 받아줄 사람인지부터 살펴보세요.",
        strategy_bubble="다가가는 속도는 충분히 조절할 수 있어요. 흐름이 그렇게 말해요.",
    ),
    # ── 정화 ───────────────────────────────────────────────────
    "정화": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="한 사람에게 깊이 빠짐", pct="74%", multiplier="두드러지게",
                         desc="한 사람에게 마음을 깊이 쏟다 보니 상처도 그만큼 커요."),
            PatternEntry(keyword="조용히 정성만 쌓음", pct="68%", multiplier="33%",
                         desc="티 내지 않고 챙기는 마음이 다른 분들보다 많은 편이에요."),
            PatternEntry(keyword="딴 데 보면 마음 닫음", pct="52%", multiplier="두드러지게",
                         desc="상대 시선이 다른 데로 향한다 느끼면 마음을 닫아버려요."),
        ),
        strategies=(
            ControlStrategy(keyword="마음 슬쩍 드러내기",
                            desc="조용히 쌓아둔 정성을 한 주 두어 번이라도 표현해보기. 상대가 그 마음을 더 잘 알아채요.",
                            effect_pct="42%"),
            ControlStrategy(keyword="한 사람에게만 매이지 않기",
                            desc="한 사람에게 마음을 다 쏟지 않도록 여유를 두면, 멀어졌을 때 회복이 한결 빨라져요.",
                            effect_pct="36%"),
        ),
        stability_boost_pct="44%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="등불은 봐주는 사람이 있을 때 비로소 의미가 생겨요.",
        strategy_bubble="작은 표현 하나가 마음을 전하는 결정적인 차이를 만들어요.",
    ),
    # ── 무토 ───────────────────────────────────────────────────
    "무토": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="안정에 너무 매달림", pct="72%", multiplier="두드러지게",
                         desc="흔들릴 것 같은 상황이 오면 마음을 잘 안 열어요."),
            PatternEntry(keyword="속도 안 맞으면 멈춤", pct="65%", multiplier="36%",
                         desc="상대가 서두르면 따라가기보다 멈춰 서버리는 편이에요."),
            PatternEntry(keyword="믿기까지 오래 걸림", pct="59%", multiplier="두드러지게",
                         desc="상대를 마음으로 믿기까지 다른 분들보다 시간이 더 걸려요."),
        ),
        strategies=(
            ControlStrategy(keyword="작은 변화 받아들이기",
                            desc="한 주에 한 번이라도 작은 변화를 받아들여보기. 인연을 더 빨리 알아보게 돼요.",
                            effect_pct="40%"),
            ControlStrategy(keyword="믿는 과정 조금 줄이기",
                            desc="확인하고 또 확인하는 단계를 조금 덜어내면, 관계로 들어서는 속도가 한결 빨라져요.",
                            effect_pct="33%"),
        ),
        stability_boost_pct="35%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="안정은 강점이지만, 때로는 마음의 문을 닫아버리는 신호로도 작동해요.",
        strategy_bubble="작은 변화 하나가 그 안정을 무너뜨리진 않아요.",
    ),
    # ── 기토 ───────────────────────────────────────────────────
    "기토": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="늘 상대만 챙김", pct="79%", multiplier="두드러지게",
                         desc="자신보다 상대를 먼저 챙기다 보니 마음이 쉽게 지쳐요."),
            PatternEntry(keyword="내 욕구는 뒷전", pct="73%", multiplier="40%",
                         desc="정작 본인이 원하는 건 잘 말하지 않는 편이에요."),
            PatternEntry(keyword="지치면 갑자기 멈춤", pct="55%", multiplier="두드러지게",
                         desc="혼자 다 짊어지다 어느 순간 마음을 탁 닫아버리곤 해요."),
        ),
        strategies=(
            ControlStrategy(keyword="내가 원하는 것 말하기",
                            desc="한 주에 한 번이라도 본인이 바라는 걸 말해보기. 관계의 무게중심이 한결 균형 잡혀요.",
                            effect_pct="38%"),
            ControlStrategy(keyword="챙기는 데도 선 두기",
                            desc="상대를 챙기는 시간에도 적당한 선을 두면, 혼자 지쳐버리는 순간이 한참 뒤로 미뤄져요.",
                            effect_pct="45%"),
        ),
        stability_boost_pct="40%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="다 내어주는 게 사랑은 아니에요. 본인이 남아 있어야 관계도 쌓여요.",
        strategy_bubble="내 마음 한 줄이 매주 들어가야 관계가 균형을 잡아요.",
    ),
    # ── 경금 ───────────────────────────────────────────────────
    "경금": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="모호함에 빠른 결론", pct="77%", multiplier="두드러지게",
                         desc="애매한 상황이면 곧장 마음을 정리해버리는 편이에요."),
            PatternEntry(keyword="돌려 말하면 신뢰 하락", pct="64%", multiplier="37%",
                         desc="상대가 빙 둘러 말하면 믿음이 빠르게 식어버려요."),
            PatternEntry(keyword="한번 어긋나면 단호함", pct="57%", multiplier="두드러지게",
                         desc="믿음이 깨지면 다시 다가가기보다 딱 잘라 돌아서곤 해요."),
        ),
        strategies=(
            ControlStrategy(keyword="애매할 땐 하루 미루기",
                            desc="애매한 상황에서 바로 단정 짓지 말고 하루만 두고 보기. 섣부른 오해가 한결 줄어들어요.",
                            effect_pct="41%"),
            ControlStrategy(keyword="마음 솔직하게 말하기",
                            desc="속마음을 돌리지 말고 솔직하게 말로 꺼내보기. 서로의 믿음이 한결 단단해져요.",
                            effect_pct="35%"),
        ),
        stability_boost_pct="37%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="분명한 게 강점이지만, 분명함만으로는 애매한 마음을 못 읽어요.",
        strategy_bubble="하루 미루는 게 결정을 약하게 만드는 게 아니에요. 더 정확하게 보게 돕는 거예요.",
    ),
    # ── 신금 ───────────────────────────────────────────────────
    "신금": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="작은 실망도 크게 남음", pct="75%", multiplier="두드러지게",
                         desc="사소한 실망 하나도 마음속에 오래 무겁게 남는 편이에요."),
            PatternEntry(keyword="마음 여는 데 오래 걸림", pct="70%", multiplier="34%",
                         desc="처음 마음을 여는 데까지 다른 분들보다 시간이 더 걸려요."),
            PatternEntry(keyword="옛 상처가 오래감", pct="53%", multiplier="두드러지게",
                         desc="지난 상처가 마음에 꽤 오래 머물러 있곤 해요."),
        ),
        strategies=(
            ControlStrategy(keyword="실망 크기 가늠해보기",
                            desc="실망스러운 일이 생기면 그 무게를 한 번 가늠해본 뒤 반응하기. 지나치게 예민해지는 일이 줄어요.",
                            effect_pct="39%"),
            ControlStrategy(keyword="마음의 빗장 조금 풀기",
                            desc="스스로를 지키려 재는 단계를 조금만 덜어내면, 관계로 들어서는 속도가 한결 빨라져요.",
                            effect_pct="32%"),
        ),
        stability_boost_pct="36%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="섬세함이 강점이지만, 묵은 상처가 새 인연을 가로막기도 해요.",
        strategy_bubble="작은 실망 하나하나에 매번 같은 무게로 반응하지 않아도 돼요.",
    ),
    # ── 계수 ───────────────────────────────────────────────────
    "계수": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="속마음을 잘 안 내비침", pct="76%", multiplier="두드러지게",
                         desc="겉으로 잘 드러내지 않아 마음이 속에만 고여 있곤 해요."),
            PatternEntry(keyword="서두르면 흐려짐", pct="68%", multiplier="35%",
                         desc="상대가 재촉하면 마음이 흐트러지며 멀어지는 편이에요."),
            PatternEntry(keyword="몰라주면 자신감 떨어짐", pct="54%", multiplier="두드러지게",
                         desc="마음을 알아봐 주지 않으면 스스로에 대한 믿음이 빠르게 줄어요."),
        ),
        strategies=(
            ControlStrategy(keyword="속마음 하나씩 꺼내기",
                            desc="담아둔 마음 하나를 한 주에 한 번씩 표현해보기. 상대가 그 마음을 더 잘 알아채요.",
                            effect_pct="43%"),
            ControlStrategy(keyword="내 가치 차분히 돌아보기",
                            desc="남의 반응에만 흔들리지 말고 스스로를 차분히 돌아보면, 마음이 한결 단단해져요.",
                            effect_pct="37%"),
        ),
        stability_boost_pct="39%",
        blockade_bubble="정리해보니 보이네요. {USER_NAME}님 사주는 {OHANG_EXCESS} 기운이 강한 편이에요.",
        pattern_bubble="속마음은 본인 안에서만 보여요. 밖으로 꺼내야 상대도 알아봐요.",
        strategy_bubble="작은 표현 하나가 마음이 전해지는 결정적 차이를 만들어요.",
    ),
}


VALID_DOYOON_P3_ILGAN: frozenset[str] = frozenset(DOYOON_P3_DATA.keys())
VALID_DOYOON_P3_OHANG: frozenset[str] = frozenset(BLOCKADE_BY_OHANG.keys())
