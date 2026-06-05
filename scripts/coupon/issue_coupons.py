"""100% 무료 쿠폰 N장 발급 — DB(coupons)에 ACTIVE 로 insert.

전제: alembic upgrade head 로 coupons 테이블 생성 완료, MySQL 기동 중.
⚠️ 발급은 "그 환경의 DB"에 들어간다 — 실고객용은 prod DB(EC2) 에서 실행해야 함.

실행 예:
    python -X utf8 -m scripts.coupon.issue_coupons --count 20 --memo insta_review
    python -X utf8 -m scripts.coupon.issue_coupons --count 1 --memo cs_2026_06

출력: 발급된 코드를 stdout 에 한 줄씩(DM 복붙용), 요약은 stderr.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime

# 전체 ORM 등록 — coupons.used_by_user_id FK 의 대상 users 테이블이 메타데이터에
# 있어야 flush 가 가능(standalone 스크립트는 main.py 처럼 base 를 거치지 않으므로 명시 import).
import app.infrastructure.database.base  # noqa: E402,F401
from app.domains.payment.adapter.outbound.persistence.coupon_repository import (
    CouponRepository,
)
from app.domains.payment.domain.entity.coupon import Coupon
from app.domains.payment.domain.service.coupon_code_generator import (
    generate_coupon_code,
)
from app.infrastructure.database.session import AsyncSessionLocal

_MAX_RETRY_PER_CODE = 5


async def _issue(count: int, memo: str | None, prefix: str) -> list[str]:
    issued: list[str] = []
    async with AsyncSessionLocal() as session:
        repo = CouponRepository(session)
        for _ in range(count):
            code = ""
            for _attempt in range(_MAX_RETRY_PER_CODE):
                candidate = generate_coupon_code(prefix)
                if await repo.find_by_code(candidate) is None:
                    code = candidate
                    break
            if not code:
                raise RuntimeError("코드 유니크 충돌 — 재시도 한도 초과")
            await repo.save(
                Coupon.issue(code=code, created_at=datetime.now(UTC), memo=memo)
            )
            issued.append(code)
        await session.commit()
    return issued


def main() -> None:
    parser = argparse.ArgumentParser(description="100% 무료 쿠폰 발급")
    parser.add_argument("--count", type=int, required=True, help="발급할 쿠폰 수")
    parser.add_argument(
        "--memo", type=str, default=None, help="용도 메모 (예: insta_review, cs_2026_06)"
    )
    parser.add_argument("--prefix", type=str, default="DOHWA", help="코드 prefix")
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count 는 1 이상이어야 합니다.")

    codes = asyncio.run(_issue(args.count, args.memo, args.prefix))

    # 코드는 stdout (복붙용), 요약은 stderr
    for code in codes:
        print(code)
    print(
        f"[issue] {len(codes)}장 발급 완료 (memo={args.memo})",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
