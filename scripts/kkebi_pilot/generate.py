"""async claude -p subprocess 호출 + 디스크 캐시 + 재시도.

캐시 키: {slot}_{stage}_{key_repr}.json
재실행 시 캐시 적중하면 호출 X.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import sys
import time
from pathlib import Path

from .prompts import SLOTS, MOOD3_KR
from .matrix import AREA_KOREAN, TIME_KOREAN

PILOT_ROOT = Path(__file__).resolve().parent
CACHE_DIR = PILOT_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

MAX_CONCURRENCY = 3  # rate limit 보수적
RETRY_MAX = 5
RETRY_BACKOFF_SECONDS = (10, 30, 90, 240, 600)  # rate limit 풀릴 충분한 여유


def _cache_path(slot: str, stage: int, key: dict) -> Path:
    key_str = json.dumps(key, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha1(key_str.encode("utf-8")).hexdigest()[:10]
    return CACHE_DIR / f"{slot}_s{stage}_{h}.json"


def _format_prompt(template: str, key: dict, stage1_output: str | None = None) -> str:
    fmt_args = dict(key)
    # 한국어 표기 자동 매핑
    if "time_slot" in fmt_args:
        fmt_args["time_slot_kr"] = TIME_KOREAN.get(fmt_args["time_slot"], fmt_args["time_slot"])
    if "area" in fmt_args:
        fmt_args["area_kr"] = AREA_KOREAN.get(fmt_args["area"], fmt_args["area"])
    if "mood3" in fmt_args:
        fmt_args["mood3_kr"] = MOOD3_KR.get(fmt_args["mood3"], fmt_args["mood3"])
    if stage1_output is not None:
        fmt_args["stage1_output"] = stage1_output
    return template.format(**fmt_args)


async def _call_claude(prompt: str, semaphore: asyncio.Semaphore, model: str = "sonnet") -> str:
    async with semaphore:
        for attempt in range(RETRY_MAX):
            try:
                # claude -p prompt: 표준입력으로 prompt 전달
                # Windows에서 claude가 .cmd라 shell 호출 필요
                proc = await asyncio.create_subprocess_shell(
                    f"claude -p --model {model}",
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate(prompt.encode("utf-8"))
                if proc.returncode == 0:
                    text = stdout.decode("utf-8", errors="replace").strip()
                    if text:
                        return text
                # 실패 시 백오프
                err = stderr.decode("utf-8", errors="replace")[:200]
                if attempt < RETRY_MAX - 1:
                    wait = RETRY_BACKOFF_SECONDS[attempt]
                    print(f"  [retry] claude -p 실패 (attempt {attempt+1}): {err[:80]} → {wait}s 대기", file=sys.stderr)
                    await asyncio.sleep(wait)
                else:
                    raise RuntimeError(f"claude -p 최종 실패: {err}")
            except Exception as e:
                if attempt < RETRY_MAX - 1:
                    wait = RETRY_BACKOFF_SECONDS[attempt]
                    print(f"  [retry] 예외 (attempt {attempt+1}): {e} → {wait}s 대기", file=sys.stderr)
                    await asyncio.sleep(wait)
                else:
                    raise
        raise RuntimeError("재시도 한도 초과")


async def generate_cell(
    slot: str,
    key: dict,
    semaphore: asyncio.Semaphore,
    stats: dict,
) -> str:
    """슬롯 1셀 → 1단계 + 2단계 → 최종 텍스트. 캐시 적중 시 즉시 반환."""
    # 1단계
    cache1 = _cache_path(slot, 1, key)
    if cache1.exists():
        stage1_out = json.loads(cache1.read_text(encoding="utf-8"))["output"]
        stats["cache_hits"] += 1
    else:
        prompt1 = _format_prompt(SLOTS[slot]["stage1"], key)
        t0 = time.time()
        stage1_out = await _call_claude(prompt1, semaphore, model="sonnet")
        cache1.write_text(json.dumps({"key": key, "prompt": prompt1, "output": stage1_out},
                                     ensure_ascii=False, indent=2), encoding="utf-8")
        stats["calls"] += 1
        stats["total_seconds"] += time.time() - t0

    # 2단계
    cache2 = _cache_path(slot, 2, key)
    if cache2.exists():
        stage2_out = json.loads(cache2.read_text(encoding="utf-8"))["output"]
        stats["cache_hits"] += 1
    else:
        prompt2 = _format_prompt(SLOTS[slot]["stage2"], key, stage1_output=stage1_out)
        t0 = time.time()
        stage2_out = await _call_claude(prompt2, semaphore, model="haiku")
        cache2.write_text(json.dumps({"key": key, "stage1": stage1_out, "prompt": prompt2, "output": stage2_out},
                                     ensure_ascii=False, indent=2), encoding="utf-8")
        stats["calls"] += 1
        stats["total_seconds"] += time.time() - t0

    return stage2_out


async def generate_user_result(user, slot_keys: dict, semaphore: asyncio.Semaphore, stats: dict) -> dict:
    """한 사용자의 모든 슬롯 셀 생성."""
    cells = slot_keys["cells"]
    sipseong = slot_keys["sipseong"]
    branch_rel = slot_keys["branch_rel"]

    tasks = {}

    # A 헤드라인
    tasks["A"] = asyncio.create_task(generate_cell("A", {"sipseong": sipseong, "branch_rel": branch_rel}, semaphore, stats))

    # B/C 시간대
    for ts, m in cells["B_time"]:
        tasks[f"B_{ts}"] = asyncio.create_task(generate_cell("B", {"time_slot": ts, "mood3": m}, semaphore, stats))
    for ts, m in cells["C_time_tip"]:
        tasks[f"C_{ts}"] = asyncio.create_task(generate_cell("C", {"time_slot": ts, "mood3": m}, semaphore, stats))

    # D/E/F/G 영역
    for area, m in cells["D_area_head"]:
        tasks[f"D_{area}"] = asyncio.create_task(generate_cell("D", {"area": area, "mood3": m}, semaphore, stats))
    for area, ss in cells["E_bok"]:
        tasks[f"E_{area}"] = asyncio.create_task(generate_cell("E", {"area": area, "sipseong": ss}, semaphore, stats))
    for area, ss in cells["F_gyeong"]:
        tasks[f"F_{area}"] = asyncio.create_task(generate_cell("F", {"area": area, "sipseong": ss}, semaphore, stats))
    for area, ss in cells["G_jo"]:
        tasks[f"G_{area}"] = asyncio.create_task(generate_cell("G", {"area": area, "sipseong": ss}, semaphore, stats))

    results = {}
    for label, task in tasks.items():
        results[label] = await task
    return results
