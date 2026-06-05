"""캐릭터별 결제 가격 마스터 — BE 단일 진실원.

PayApp 플로에서는 FE가 가격을 보낼 필요 없음. BE가 character 만 받아서 가격 결정.
가격 위변조 차단 + 단일 관리 지점.
"""

from app.domains.payment.domain.value_object.payment_status import CharacterCode

# 론칭 할인가 — 정가 20,000원 → 판매가 4,900원 (연우·도윤 공통).
# 정가(20,000)는 FE 표시 전용(취소선)이고, 실제 결제 금액의 단일 진실원은 이 값이다.
# FE checkoutProducts.ts 의 priceKrw 와 반드시 동일하게 유지할 것.
_CHARACTER_PRICES_KRW: dict[CharacterCode, int] = {
    CharacterCode.YEONWOO: 4900,
    CharacterCode.DOYOON: 4900,
}

_CHARACTER_GOODS_NAMES: dict[CharacterCode, str] = {
    CharacterCode.YEONWOO: "강연우의 정통 연애 사주",
    CharacterCode.DOYOON: "한도윤의 데이터 기반 연애분석",
}


def get_character_price(character: CharacterCode) -> int:
    if character not in _CHARACTER_PRICES_KRW:
        raise ValueError(f"가격이 정의되지 않은 캐릭터: {character}")
    return _CHARACTER_PRICES_KRW[character]


def get_character_goods_name(character: CharacterCode) -> str:
    if character not in _CHARACTER_GOODS_NAMES:
        raise ValueError(f"상품명이 정의되지 않은 캐릭터: {character}")
    return _CHARACTER_GOODS_NAMES[character]
