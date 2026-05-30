"""70장 전수 검증 + 리포트 생성.

- 도메인어 누출 (개선된 check_leak)
- JSON 구조 완전성
- 슬롯별 길이 규칙
- 헤드라인 70개 나열 / 슬롯별 톤 비교

실행: python -X utf8 -m scripts.kkebi_gen.verify
산출: 깨비_무료사주/pilot/VERIFY_70.md
"""
from __future__ import annotations

import json
from pathlib import Path

from .generate import AREA_KEYS, _validate
from .prompt_builder import iter_combos

CACHE = Path(__file__).resolve().parent / "cache"
OUT = Path(__file__).resolve().parents[2].parent / "깨비_무료사주" / "pilot" / "VERIFY_70.md"

# 길이 규칙 (글자수)
LEN_RULES = {
    "headline": (10, 40),
    "area_summary": (10, 32),
    "area_block": (50, 170),   # bok/gyeong/jo
    "time_comment": (4, 16),
    "time_tip": (10, 45),
}


def _len_problems(body: dict) -> list[str]:
    p = []
    h = body.get("headline", "")
    lo, hi = LEN_RULES["headline"]
    if not (lo <= len(h) <= hi):
        p.append(f"headline 길이 {len(h)} (기대 {lo}~{hi})")
    for a in AREA_KEYS:
        ar = body.get("areas", {}).get(a, {})
        s = ar.get("summary", "")
        lo, hi = LEN_RULES["area_summary"]
        if s and not (lo <= len(s) <= hi):
            p.append(f"{a}.summary 길이 {len(s)}")
        for blk in ("bok", "gyeong", "jo"):
            t = ar.get(blk, "")
            lo, hi = LEN_RULES["area_block"]
            if t and not (lo <= len(t) <= hi):
                p.append(f"{a}.{blk} 길이 {len(t)}")
    return p


def main() -> None:
    combos = list(iter_combos())
    records = {}
    for ss, br in combos:
        cp = CACHE / f"{ss}_{br}.json"
        if cp.exists():
            records[(ss, br)] = json.loads(cp.read_text(encoding="utf-8"))

    leak_bad, struct_bad, len_bad = [], [], []
    for (ss, br), r in records.items():
        body = r["body"]
        problems = _validate(body)  # 구조 + 누출
        leaks = [p for p in problems if "누출" in p]
        struct = [p for p in problems if "누출" not in p]
        lens = _len_problems(body)
        if leaks:
            leak_bad.append((ss, br, leaks))
        if struct:
            struct_bad.append((ss, br, struct))
        if lens:
            len_bad.append((ss, br, lens))

    L = []
    L.append("# 깨비 70장 — 전수 검증 리포트")
    L.append("")
    L.append(f"- 생성: **{len(records)}/70**")
    L.append(f"- 도메인어 누출: **{len(leak_bad)}건** {'✅' if not leak_bad else '❌'}")
    L.append(f"- 구조 결함: **{len(struct_bad)}건** {'✅' if not struct_bad else '❌'}")
    L.append(f"- 길이 규칙 위반: **{len(len_bad)}건** {'✅' if not len_bad else '⚠️ (참고용)'}")
    L.append("")

    if leak_bad:
        L.append("## ❌ 도메인어 누출")
        for ss, br, ls in leak_bad:
            L.append(f"- {ss}×{br}: {ls}")
        L.append("")
    if struct_bad:
        L.append("## ❌ 구조 결함")
        for ss, br, st in struct_bad:
            L.append(f"- {ss}×{br}: {st}")
        L.append("")
    if len_bad:
        L.append("## ⚠️ 길이 규칙 위반 (참고)")
        for ss, br, ln in len_bad:
            L.append(f"- {ss}×{br}: {', '.join(ln)}")
        L.append("")

    # 헤드라인 70개
    L.append("---")
    L.append("## §A. 헤드라인 70개")
    L.append("")
    L.append("| 십성 \\ 관계 | 합 | 충 | 형 | 파 | 해 | 동주 | 보통 |")
    L.append("|---|---|---|---|---|---|---|---|")
    from .prompt_builder import BRANCH_REL, SIPSEONG
    for ss in SIPSEONG:
        row = [ss]
        for br in BRANCH_REL:
            h = records.get((ss, br), {}).get("body", {}).get("headline", "—")
            row.append(h)
        L.append("| " + " | ".join(row) + " |")
    L.append("")

    # 슬롯별 톤 비교 (조언 G — love 영역, 10개 십성 × 합 고정)
    L.append("---")
    L.append("## §B. 깨비 조언(助) 톤 비교 — 연애 영역 (관계=합 고정, 십성 10종)")
    L.append("")
    for ss in SIPSEONG:
        jo = records.get((ss, "합"), {}).get("body", {}).get("areas", {}).get("love", {}).get("jo", "—")
        L.append(f"- **{ss}**: {jo}")
    L.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"검증 완료 → {OUT}")
    print(f"누출 {len(leak_bad)} / 구조 {len(struct_bad)} / 길이 {len(len_bad)}")


if __name__ == "__main__":
    main()
