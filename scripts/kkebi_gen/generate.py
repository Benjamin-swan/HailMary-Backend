"""깨비 70장 통째 1단계 생성.

claude -p (구독 auth) 를 빈 임시 디렉토리에서 호출해 계정/프로젝트 컨텍스트를 격리하고,
--system-prompt-file 로 깨비 시스템 프롬프트를 주입, --output-format json 으로 받는다.

실행:
    # 1장 테스트
    python -X utf8 -m scripts.kkebi_gen.generate --combo 식신:합
    # 앞에서 N개
    python -X utf8 -m scripts.kkebi_gen.generate --limit 3
    # 전량
    python -X utf8 -m scripts.kkebi_gen.generate

캐시: scripts/kkebi_gen/cache/{sipseong}_{branch_rel}.json (재실행 시 적중하면 호출 X)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import tempfile
import time
from pathlib import Path

from scripts.kkebi_pilot.render import check_leak

from .prompt_builder import build_user_prompt, iter_combos

GEN_ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT_FILE = GEN_ROOT / "system_prompt.txt"
CACHE_DIR = GEN_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

MAX_CONCURRENCY = 3
RETRY_MAX = 5
RETRY_BACKOFF_SECONDS = (10, 30, 90, 240, 600)

# 본문 JSON이 가져야 할 구조
AREA_KEYS = ["love", "work", "money", "health", "study"]
TIME_KEYS = ["morning", "afternoon", "night"]


def _cache_path(sipseong: str, branch_rel: str) -> Path:
    return CACHE_DIR / f"{sipseong}_{branch_rel}.json"


def _strip_fences(text: str) -> str:
    """모델이 ```json ... ``` 코드펜스를 붙였을 때 제거."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t)
    return t.strip()


def _extract_result(stdout_text: str) -> str:
    """claude --output-format json 응답에서 모델 최종 텍스트 추출.

    응답 형태: {"type":"result","result":"<모델텍스트>", ...}
    혹시 구조가 다르면 원문을 그대로 반환(방어적).
    """
    try:
        obj = json.loads(stdout_text)
    except json.JSONDecodeError:
        return stdout_text
    if isinstance(obj, dict):
        for key in ("result", "text", "content"):
            if isinstance(obj.get(key), str):
                return obj[key]
    return stdout_text


async def _call_claude(user_prompt: str, semaphore: asyncio.Semaphore) -> dict:
    """claude -p 1회 호출 → 본문 dict 반환."""
    async with semaphore:
        for attempt in range(RETRY_MAX):
            try:
                workdir = tempfile.mkdtemp(prefix="kkebi_gen_")  # 빈 디렉토리 = CLAUDE.md 격리
                cmd = (
                    f'claude -p --system-prompt-file "{SYSTEM_PROMPT_FILE}" '
                    f'--output-format json --model sonnet'
                )
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=workdir,
                )
                stdout, stderr = await proc.communicate(user_prompt.encode("utf-8"))
                if proc.returncode == 0 and stdout.strip():
                    result_text = _extract_result(stdout.decode("utf-8", errors="replace"))
                    body = json.loads(_strip_fences(result_text))
                    return body
                err = stderr.decode("utf-8", errors="replace")[:200]
                raise RuntimeError(f"claude 실패 rc={proc.returncode}: {err}")
            except Exception as e:
                if attempt < RETRY_MAX - 1:
                    wait = RETRY_BACKOFF_SECONDS[attempt]
                    print(f"  [retry {attempt+1}] {e} → {wait}s 대기", file=sys.stderr)
                    await asyncio.sleep(wait)
                else:
                    raise
        raise RuntimeError("재시도 한도 초과")


def _validate(body: dict) -> list[str]:
    """구조 + 도메인 누출 검사. 문제 메시지 리스트(빈 리스트면 통과)."""
    problems = []
    if "headline" not in body:
        problems.append("headline 없음")
    areas = body.get("areas", {})
    for a in AREA_KEYS:
        if a not in areas:
            problems.append(f"areas.{a} 없음")
            continue
        for f in ("summary", "bok", "gyeong", "jo"):
            if not areas[a].get(f):
                problems.append(f"areas.{a}.{f} 비어있음")
    tf = body.get("timeFlow", {})
    for t in TIME_KEYS:
        if t not in tf:
            problems.append(f"timeFlow.{t} 없음")
            continue
        for f in ("comment", "tip"):
            if not tf[t].get(f):
                problems.append(f"timeFlow.{t}.{f} 비어있음")
    # 도메인 누출: 모든 문자열 값 검사
    for leaked in _all_strings(body):
        leaks = check_leak(leaked)
        if leaks:
            problems.append(f"도메인어 누출: {leaks} in «{leaked[:30]}»")
    return problems


def _all_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _all_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _all_strings(v)


async def generate_one(sipseong: str, branch_rel: str, semaphore: asyncio.Semaphore,
                       redo: bool = False) -> tuple[dict, bool]:
    """1조합 생성. (본문, cache_hit) 반환."""
    cp = _cache_path(sipseong, branch_rel)
    if cp.exists() and not redo:
        return json.loads(cp.read_text(encoding="utf-8"))["body"], True

    prompt = build_user_prompt(sipseong, branch_rel)
    t0 = time.time()
    body = await _call_claude(prompt, semaphore)
    elapsed = time.time() - t0

    problems = _validate(body)
    record = {
        "sipseong": sipseong,
        "branch_rel": branch_rel,
        "body": body,
        "problems": problems,
        "elapsed": round(elapsed, 1),
    }
    cp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    flag = "⚠️" if problems else "✅"
    print(f"  {flag} {sipseong}:{branch_rel} ({elapsed:.0f}s)"
          + (f" — 문제 {len(problems)}건" if problems else ""), file=sys.stderr)
    return body, False


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--combo", help="단일 조합, 예: 식신:합")
    ap.add_argument("--limit", type=int, help="앞에서 N개만")
    ap.add_argument("--concurrency", type=int, default=MAX_CONCURRENCY)
    ap.add_argument("--redo", action="store_true", help="캐시 무시하고 재생성")
    args = ap.parse_args()

    if args.combo:
        ss, br = args.combo.split(":")
        combos = [(ss, br)]
    else:
        combos = list(iter_combos())
        if args.limit:
            combos = combos[: args.limit]

    sem = asyncio.Semaphore(args.concurrency)
    print(f"[kkebi_gen] {len(combos)}조합 생성 시작 (동시도={args.concurrency})", file=sys.stderr)
    t0 = time.time()

    tasks = [generate_one(ss, br, sem, redo=args.redo) for ss, br in combos]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    ok = sum(1 for r in results if not isinstance(r, Exception))
    fail = len(results) - ok
    print(f"[kkebi_gen] 완료 — 성공 {ok} / 실패 {fail} / 벽시계 {time.time()-t0:.0f}s",
          file=sys.stderr)
    if fail:
        for (ss, br), r in zip(combos, results, strict=False):
            if isinstance(r, Exception):
                print(f"  ✗ {ss}:{br} — {r}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
