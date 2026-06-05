"""쿠폰 코드 생성·정규화 — 순수 Python 도메인 서비스.

인스타 DM 으로 뿌리기 쉽도록 사람-친화적이면서, 추측 불가능해야 한다.
혼동되는 글자(0/O, 1/I/L)는 알파벳에서 제외.
"""

import secrets

# 혼동 글자 제거: 0, O, 1, I, L 없음 → 31자
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789".replace("L", "")
_BODY_LEN = 8
_DEFAULT_PREFIX = "DOHWA"


def generate_coupon_code(prefix: str = _DEFAULT_PREFIX) -> str:
    """`DOHWA-XXXX-XXXX` 형태의 코드 생성. 약 39비트 엔트로피.

    secrets 사용(예측 가능한 random 금지).
    """
    body = "".join(secrets.choice(_ALPHABET) for _ in range(_BODY_LEN))
    return f"{prefix.upper()}-{body[:4]}-{body[4:]}"


def normalize_coupon_code(raw: str) -> str:
    """사용자 입력 정규화 — 대문자화 + 공백 제거. 비교·저장 시 항상 이 형태.

    하이픈은 보존(코드 형식의 일부). 앞뒤/내부 공백만 제거.
    """
    return "".join(raw.split()).upper()
