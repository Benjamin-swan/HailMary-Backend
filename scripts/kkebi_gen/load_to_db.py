"""생성된 70장(cache/*.json) → daily_templates 테이블 적재.

전제: alembic upgrade head 로 daily_templates 테이블 생성 완료, MySQL 기동 중.
실행: python -X utf8 -m scripts.kkebi_gen.load_to_db

이미 있는 (sipseong, branch_rel) 는 body 갱신(upsert), 없으면 insert.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import select

from app.domains.kkebi.infrastructure.orm.daily_template_orm import DailyTemplateORM
from app.infrastructure.database.session import AsyncSessionLocal

CACHE = Path(__file__).resolve().parent / "cache"


async def main() -> None:
    files = sorted(CACHE.glob("*.json"))
    if not files:
        print("cache 비어있음 — 먼저 generate 실행", file=sys.stderr)
        return

    inserted = updated = skipped = 0
    async with AsyncSessionLocal() as session:
        for f in files:
            rec = json.loads(f.read_text(encoding="utf-8"))
            ss, br, body = rec["sipseong"], rec["branch_rel"], rec["body"]
            if rec.get("problems"):
                print(f"  ⚠️ {ss}:{br} 문제 있음 — 적재 제외: {rec['problems']}", file=sys.stderr)
                skipped += 1
                continue

            existing = (await session.execute(
                select(DailyTemplateORM).where(
                    DailyTemplateORM.sipseong == ss,
                    DailyTemplateORM.branch_rel == br,
                )
            )).scalar_one_or_none()

            if existing:
                existing.body = body
                updated += 1
            else:
                session.add(DailyTemplateORM(sipseong=ss, branch_rel=br, body=body))
                inserted += 1
        await session.commit()

    print(f"[load] insert {inserted} / update {updated} / skip {skipped} / 총 {len(files)}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
