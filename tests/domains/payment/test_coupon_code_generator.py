"""coupon_code_generator 단위 테스트.

대상:
    1. 형식 — PREFIX-XXXX-XXXX
    2. 혼동 글자(0 O 1 I L) 미포함
    3. prefix 대문자화
    4. 다수 생성 시 중복 0 근사 (엔트로피)
    5. normalize — 소문자/공백 정리, 하이픈 보존
"""

import re

from app.domains.payment.domain.service.coupon_code_generator import (
    generate_coupon_code,
    normalize_coupon_code,
)

_FORBIDDEN = set("0O1IL")
_PATTERN = re.compile(r"^[A-Z]+-[A-Z2-9]{4}-[A-Z2-9]{4}$")


def test_format_matches_pattern() -> None:
    code = generate_coupon_code()
    assert code.startswith("DOHWA-")
    assert _PATTERN.match(code), code


def test_no_confusing_characters() -> None:
    body = "".join(generate_coupon_code().split("-")[1:])
    for _ in range(200):
        body += "".join(generate_coupon_code().split("-")[1:])
    assert not (_FORBIDDEN & set(body)), "혼동 글자(0 O 1 I L) 가 코드에 없어야 함"


def test_prefix_uppercased() -> None:
    code = generate_coupon_code(prefix="cs")
    assert code.startswith("CS-")


def test_generates_unique_codes() -> None:
    codes = {generate_coupon_code() for _ in range(500)}
    assert len(codes) > 490, "엔트로피상 500개 중 중복 거의 없어야 함"


def test_normalize_strips_spaces_and_uppercases() -> None:
    assert normalize_coupon_code("  dohwa-abcd-2345 ") == "DOHWA-ABCD-2345"
    assert normalize_coupon_code("dohwa abcd 2345") == "DOHWAABCD2345"
