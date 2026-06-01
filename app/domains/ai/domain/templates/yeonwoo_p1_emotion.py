"""P-1 1-3 연애 중 감정 패턴 — 풀 템플릿 합성.

명리학 도메인 활용:
- 일간 10 × 촛불 차트 (3 row: 초반/중반/위기, 각 row의 강도/개수 다름)
- 일간 10 × row별 desc (30 조각)
- 일간 10 × ai_emotion 3단락 (30 조각)
- peak 위치 (분홍 강조 row) 일간별 다름

핵심 패턴:
- 갑목 (직진 단단): 초반부터 강 → 위기 단호 끊음 (위기 peak)
- 을목 (감김): 천천히 감김 → 위기 오래 끔 (위기 peak)
- 병화 (빛 → 식음): 초반 가장 강 → 위기 사라짐 (역행, 초반 peak)
- 정화 (은근 집중): 변동 X, 한 사람만 (peak X)
- 무토 (한결같음): 일관 (peak X)
- 기토 (다정 키움): 점점 키움 (위기 peak)
- 경금 (결단): 강함 유지 → 위기 단호 끊음 (위기 peak)
- 신금 (자존): 거리 → 들임 → 자존심 상함 (위기 peak)
- 임수 (깊이 빠짐): 누진 (위기 peak, HTML 더미)
- 계수 (스며듦): 천천히 → 위기 멈출 수 없음 (위기 peak)

AI 호출 0.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandleStage:
    label: str
    flames: tuple[str, ...]
    desc: str
    is_peak: bool


# ── 일간별 촛불 차트 패턴 (3 row) + row별 desc ──
CANDLE_PATTERN_BY_ILGAN: dict[str, tuple[CandleStage, CandleStage, CandleStage]] = {
    "갑목": (
        CandleStage("초반", ("weak", "medium"),
                    "망설임 없이 표현하고 원하는 걸 분명히 말해.", False),
        CandleStage("중반", ("weak", "medium", "strong"),
                    "더 흔들림 없이 단단하고 우직하게 다가가.", False),
        CandleStage("후반", ("weak",),
                    "안 맞다 싶으면 단호하게 끊어버리지. 미련도 없어.", True),
    ),
    "을목": (
        CandleStage("초반", ("weak",),
                    "상대에게 서서히 감기기 시작하는 거야. 자신도 모르게.", False),
        CandleStage("중반", ("weak", "medium"),
                    "점점 깊이 들어가니까 빠져나오기 어려워져.", False),
        CandleStage("후반", ("weak", "medium", "medium"),
                    "떠나고도 오래 감정이 남아서 회복이 느려.", True),
    ),
    "병화": (
        CandleStage("초반", ("strong", "strong", "strong"),
                    "한 번에 거리낌 없이 환하게 비춰.", True),
        CandleStage("중반", ("weak", "medium"),
                    "조금씩 식어가. 이건 익숙해지고 있는 거야.", False),
        CandleStage("후반", ("weak",),
                    "한꺼번에 사라져. 상대는 차가워졌다고 느끼겠지.", False),
    ),
    "정화": (
        CandleStage("초반", ("weak",),
                    "작은 불꽃이지만 우직한 느낌도 있어. 한 사람만 보거든.", False),
        CandleStage("중반", ("weak", "weak"),
                    "그 사람만 데우는 거야. 흔들림 없이.", False),
        CandleStage("후반", ("weak", "weak", "weak"),
                    "한 사람한테 집중해. 넌 쉽게 바뀌지 않거든.", False),
    ),
    "무토": (
        CandleStage("초반", ("medium",),
                    "묵묵히 자리 잡고 있어. 미동도 없이.", False),
        CandleStage("중반", ("medium", "medium"),
                    "한결같이 곁에 있어주고, 행동으로 증명해.", False),
        CandleStage("후반", ("medium", "medium", "medium"),
                    "한 번 결정하면 안 흔들려.", False),
    ),
    "기토": (
        CandleStage("초반", ("weak",),
                    "조금씩 챙겨주기 시작해.", False),
        CandleStage("중반", ("weak", "medium"),
                    "점점 더 천천히 깊어지고 진심이 쌓여.", False),
        CandleStage("후반", ("strong", "strong", "strong"),
                    "너 자신을 잊을 만큼 줘. 그러다 무너지는 거야.", True),
    ),
    "경금": (
        CandleStage("초반", ("strong",),
                    "강하게 다가가서 너를 분명하게 인식시켰어.", False),
        CandleStage("중반", ("strong", "medium"),
                    "흔들림이 전혀 없다.", False),
        CandleStage("후반", ("strong",),
                    "단호하게 끊어내네 미련이 없다. 이건 좋네.", True),
    ),
    "신금": (
        CandleStage("초반", ("weak",),
                    "거리를 두고 살펴봐.", False),
        CandleStage("중반", ("weak", "medium"),
                    "점점 마음에 들이게 돼. 그래도 경계는 하고 있어.", False),
        CandleStage("후반", ("weak",),
                    "자존심 상하면 한 번에 끊어버렸지. 되려 마음에 깊이 남았을 거야.", True),
    ),
    "임수": (
        CandleStage("초반", ("weak",),
                    "잔잔해. 아직 불꽃이 작아.", False),
        CandleStage("중반", ("weak", "medium"),
                    "타오르기 시작하면 걷잡기 어려워.", False),
        CandleStage("후반", ("weak", "medium", "strong"),
                    "걷잡을 수 없어서 한꺼번에 터지겠다.", True),
    ),
    "계수": (
        CandleStage("초반", ("weak",),
                    "거의 없는 듯 시작해. 천천히.", False),
        CandleStage("중반", ("weak", "weak"),
                    "천천히 스며드는데, 멈출 수 없어.", False),
        CandleStage("후반", ("weak", "medium", "medium"),
                    "깊이 들어가서 모든 틈을 채웠어.", True),
    ),
}


# ── AI 박스 ai_emotion 일간별 3단락 ──
PARA_1_INTRO_BY_ILGAN: dict[str, str] = {
    "갑목": "상대를 향한 마음에 불을 붙이면 넌 처음부터 망설임 없이 직진해. 그게 매력이지만 위험해.",
    "을목": "상대를 향한 마음에 불을 붙이면 넌 아주 천천히 타. 감김이 느린데, 한 번 감기면 풀기 어렵지.",
    "병화": "상대를 향한 마음에 불을 붙이면 너는 한낮의 해처럼 환해. 처음이 가장 뜨거워. 근데 식으면 한꺼번에 사라져서 문제야.",
    "정화": "상대를 향한 마음에 불을 붙이면 너는 한 사람만 데워. 안 흔들리고, 안 꺼져.",
    "무토": "상대를 향한 마음에 불을 붙여도 너는 한결같아. 변함 없이, 묵직해.",
    "기토": "상대를 향한 마음에 불을 붙이면 너는 옆 사람을 계속 챙기려고 하기 시작해. 진심을 쌓아가는 거야.",
    "경금": "상대를 향한 마음에 불을 붙이면 너는 단단하고 굳건해. 옳고 그름이 분명하지.",
    "신금": "상대를 향한 마음에 불을 붙어서, 마음의 온도가 오르는 거 같으면 넌 거리를 둬. 조금 떨어져서 살피는 거야.",
    "임수": (
        "상대를 향한 마음에 불을 붙이면 처음엔 작아. 손바닥만 한 불꽃이야. "
        "근데 어느 순간부터 멈출 수가 없어. 네 사랑이 그래."
    ),
    "계수": "상대를 향한 마음에 불을 붙여도 넌 눈에 잘 띄지 않아. 그러다 천천히 스며드는 거야.",
}

PARA_2_ANALYSIS_BY_ILGAN: dict[str, str] = {
    "갑목": (
        "{ilgan_with_hanja} 일간은 분명한 사람이야. 좋다는 표현도 빠르고 아니라는 표현도 빠르지. "
        "근데 그 직진이 상대를 짓누를 때가 와."
    ),
    "을목": (
        "{ilgan_with_hanja} 일간은 깊이 빠지는 사람이야. 한 명한테 다 줘버려. "
        "너 자신이 먼저 닳아버릴 만큼."
    ),
    "병화": (
        "{ilgan_with_hanja} 일간은 표현이 빠르고 숨김없어. 빛나는 성향인데, "
        "식는 순간 단번에 차가워져. 그게 약점이야."
    ),
    "정화": (
        "{ilgan_with_hanja} 일간은 집중형이야. 한 사람한테 정성을 끝까지 쏟아. "
        "그래서 오히려 얕은 바람 한 번에도 흔들리는 예민함이 있어."
    ),
    "무토": (
        "{ilgan_with_hanja} 일간은 다 받아주는 사람이야. 표현은 적은데 행동으로 증명해. "
        "흔들림 없는 산처럼 우직하지."
    ),
    "기토": (
        "{ilgan_with_hanja} 일간은 받기보다 주는 데 익숙해. "
        "그러다 자기를 잊는 게 약점이야."
    ),
    "경금": (
        "{ilgan_with_hanja} 일간은 결단력 있어. 아닌 관계는 잘라내. "
        "그러다 사람을 다치게 하기도 해. 너 스스로를 잘 갈고 닦아야 해."
    ),
    "신금": (
        "{ilgan_with_hanja} 일간은 은근한 자존감이 매력으로 돌지. "
        "감정을 들키지 않으려는 성향도 있어."
    ),
    "임수": (
        "{ilgan_with_hanja} 일간은 표현이 늦어. 속에선 이미 활활 타고 있는데 밖에서는 안 보이는 거야. "
        "그러다 위기가 오면 한꺼번에 터져버리지. 스스로도 놀랐을 걸."
    ),
    "계수": (
        "{ilgan_with_hanja} 일간은 분위기와 감정을 먼저 읽는 성향이야. "
        "느리게 자리를 잡지만, 그만큼 자연스럽게 스며들어서 사람들이 깨달았을 때는 이미 빠진 뒤겠다."
    ),
}

# ── 강연우 클로징 멘트 (1-3 섹션 끝 YeonwooBubble) ──
BUBBLE_BY_ILGAN: dict[str, str] = {
    "갑목": "네 직진이 너무 빨라서 상대가 따라오기 전에 부담을 느끼는 거야.",
    "을목": "너는 깊어지고 있는데, 상대는 아직 너에 대한 마음이 확실하지 않아.",
    "병화": "네가 주던 관심이 한꺼번에 식으면 상대는 이유도 모르고 차가워졌다고 느껴.",
    "정화": "네 작은 불꽃을 알아주는 사람한테만 가. 흔들리는 바람에 너무 신경을 곤두세우지 마.",
    "무토": "표현 적은 게 너의 성향인데, 상대는 그걸 무관심으로 오해할 수 있겠다.",
    "기토": "너 스스로부터 챙겨야 오래 가. 다 줘버리고 무너지지 마. 그거야말로 지 팔자 지가 꼰 거니까.",
    "경금": "끊어낼 땐 상대의 마음도 같이 끊어진다는 걸 잊지 마.",
    "신금": "자존심에 한 번 상처 입으면 너는 다시 안 돌아봐. 그러니까 처음부터 사람 잘 봐.",
    "임수": "속에서 다 끓는데 밖으로 안 내보내잖아. 상대는 네가 관심 없는 줄 알아.",
    "계수": "천천히 스며들면서 너부터 잃지 마. 흐른다고 다 받아들이지 마.",
}


def get_emotion_bubble(ilgan: str) -> str:
    """1-3 섹션 끝 강연우 멘트 (일간별)."""
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    return BUBBLE_BY_ILGAN[ilgan]


PARA_3_ADVICE_BY_ILGAN: dict[str, str] = {
    "갑목": "한 번쯤은 휘어질 줄 아는 게 좋아. 곧음만으론 사람이 못 견뎌. 너의 감정도 가끔은 천천히 가.",
    "을목": "상대에게 감겼더라도 너부터 챙겨. 끝까지 갈 수 있는 성향이니까 자신을 믿어.",
    "병화": "그늘도 같이 줘야 사람이 머물러. 빛만 너무 세면 상대가 피하려고 할 거야.",
    "정화": "네 불꽃을 알아주는 사람한테만 가. 지나치게 거센 바람은 너를 꺼버릴 테니까.",
    "무토": "다 받아주다 네가 무너지지만 마. 산도 가끔은 비를 흘려보내야 해.",
    "기토": "네가 품은 마음도 좋지만, 너를 꼭 우선시하도록 해. 너부터 챙겨야 오래 가.",
    "경금": "갈고 다듬어서 쓰되, 조심해. 아까도 말했듯 날카로워서 주변 사람이 다치기 쉬워.",
    "신금": "네 빛을 알아보는 사람한테만 곁을 줘. 험하게 다루는 손은 끊어내. 그게 안 되면 네 팔자 네가 꼬는 거야.",
    "임수": (
        "그 전에 작은 불꽃이라도 보여줘. 한 줄, 한 마디면 돼. "
        "안 그러면 상대는 영영 몰라. 너는 또 혼자 끓다가 혼자 무너질 거야."
    ),
    "계수": "흐른다고 다 받아들이지 마. 멈춰야 할 자리는 멈춰. 너부터 지켜야 해.",
}


VALID_ILGAN: frozenset[str] = frozenset(CANDLE_PATTERN_BY_ILGAN.keys())


# ── 한자 병기 헬퍼 (yeonwoo_p1_chapter_opening / yeonwoo_p1_trigger와 동일) ──
_HEAVEN_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}

_OHANG_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}


def _ilgan_with_hanja(ilgan: str) -> str:
    if len(ilgan) != 2:
        return ilgan
    h = _HEAVEN_HANJA.get(ilgan[0])
    o = _OHANG_HANJA.get(ilgan[1])
    if not h or not o:
        return ilgan
    return f"{ilgan}({h}{o})"


def get_candle_pattern(
    ilgan: str,
) -> tuple[CandleStage, CandleStage, CandleStage]:
    """일간별 감정 차트 3 row (초반/중반/위기) 반환."""
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    return CANDLE_PATTERN_BY_ILGAN[ilgan]


def compose_p1_emotion(*, ilgan: str) -> str:
    """1-3 AI 박스 ai_emotion 합성 — 250~300자.

    3단락: 도입 + 일간 분석 + 조언.
    """
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    para1 = PARA_1_INTRO_BY_ILGAN[ilgan]
    para2 = PARA_2_ANALYSIS_BY_ILGAN[ilgan].format(
        ilgan_with_hanja=_ilgan_with_hanja(ilgan)
    )
    para3 = PARA_3_ADVICE_BY_ILGAN[ilgan]

    return "\n\n".join([para1, para2, para3])
