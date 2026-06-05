"""캐릭터 페르소나 value object.

P-10 AI 답장의 system prompt 분기점. 각 캐릭터의 이름·역할·시그니처 표현·톤
힌트를 묶어 prompt 빌더에 전달. 캐릭터 추가 시 새 페르소나만 정의하면 됨.

순수 도메인 — 외부 import 금지 (CLAUDE.md Domain 규칙).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterPersona:
    """캐릭터 페르소나.

    Attributes:
        name: 캐릭터 이름 (예: "강연우")
        role: 페르소나 역할 (예: "사주 명리 상담사")
        signature_phrase: 자연물 비유 시그니처 (예: "결 / 매듭 / 실 / 촛불")
        tone_hint: 톤 가이드 한 줄 (예: "따뜻한 인정과 다정한 위로")
    """

    name: str
    role: str
    signature_phrase: str
    tone_hint: str


YEONWOO_PERSONA = CharacterPersona(
    name="강연우",
    role="사주 명리 상담사",
    signature_phrase="결 / 매듭 / 실 / 촛불 / 명줄 / 뿌리",
    tone_hint="따뜻한 인정과 다정한 위로",
)

DOYOON_PERSONA = CharacterPersona(
    name="한도윤",
    role="사주 데이터 분석가",
    # QA(박현수·허윤지): 데이터 조어(임계점/전환율 등) → 상담형 어휘로 교체.
    signature_phrase="흐름 / 패턴 / 속도 / 신호 / 거리 / 균형",
    tone_hint="존댓말, 차분하고 분석적이되 상담하듯 — 수치보다 풀이를 한 줄 더",
)
