"""파일럿 entrypoint.

실행: cd HailMary-Backend && python -m scripts.kkebi_pilot.run
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

from .generate import generate_user_result, MAX_CONCURRENCY
from .matrix import slot_keys_for_user
from .render import render_pilot_doc
from .users import USERS

PILOT_RESULTS_PATH = Path(__file__).resolve().parents[2].parent / "깨비_무료사주" / "pilot" / "PILOT_RESULTS.md"


async def main() -> None:
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    stats = {"calls": 0, "cache_hits": 0, "total_seconds": 0.0}

    print(f"[pilot] 시작 — 10명 × 슬롯 7종, 동시도={MAX_CONCURRENCY}", file=sys.stderr)
    t0 = time.time()

    all_results = []
    for i, user in enumerate(USERS, start=1):
        print(f"[pilot] ({i}/{len(USERS)}) {user.name} ({user.day_stem}{user.day_branch}) 생성 중...", file=sys.stderr)
        slot_keys = slot_keys_for_user(user)
        cells = await generate_user_result(user, slot_keys, semaphore, stats)
        all_results.append((user, slot_keys, cells))

    elapsed = time.time() - t0
    print(f"[pilot] 완료 — 신규 호출 {stats['calls']}회 / 캐시 {stats['cache_hits']}회 / 벽시계 {elapsed:.1f}초", file=sys.stderr)

    PILOT_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    render_pilot_doc(all_results, stats, PILOT_RESULTS_PATH)
    print(f"[pilot] 산출 → {PILOT_RESULTS_PATH}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
