"""파일럿 결과 → PILOT_RESULTS.md 마크다운 합성."""
from __future__ import annotations

import re
from pathlib import Path

from .matrix import AREAS, AREA_KOREAN, TIME_SLOTS, TIME_KOREAN, score_total, score_area, score_time
from .prompts import MOOD3_KR
from .users import USERS, TODAY_DISPLAY, TODAY_STEM, TODAY_BRANCH

import re

# 도메인 누출 검증용 금칙어
# 한자는 일상어에 안 섞이므로 부분일치로 충분.
LEAK_BANNED_HANJA = [
    "甲","乙","丙","丁","戊","己","庚","辛","壬","癸",
    "子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥",
    "木","火","土","金","水",
]
# 십성/메타 한글어. 부분일치하면 동사어미("다듬어지지"의 "지지")나
# 합성어("일주일"의 "일주")에 오탐 → 단어 경계 기반 정밀 매칭.
LEAK_BANNED_KO = [
    "비견","겁재","식신","상관","편재","정재","편관","정관","편인","정인",
    "사주","오행","천간","지지","일진","일주","시진","세운","대운","명리","만세력",
]
# 짧은 한글 금칙어는 일상어와 충돌하므로, 누출이 아닌 '알려진 패턴'을 먼저 가린 뒤 검사한다.
#  - "지지": 피동/사동 어미 "~어지지/~아지지/~여지지/해지지/워지지" (다듬어지지, 좋아지지, 싶어지지만…)
#           → 앞에 한글이 붙은 '...지지'는 동사 활용으로 보고 제외 (단독 '지지'만 누출로 판정)
#  - "세운": 동사 '세우다'의 관형형 "세운 계획/세운 목표" (처음에 세운 계획…)
#           → '세운' 뒤에 명사가 바로 붙으면 동사 활용으로 보고 제외
#  - "일주": 합성어 "일주일/일주년/일주간/일주마다"
_FALSE_POSITIVE = re.compile(r"[가-힣]지지|세운(?=\s*[가-힣])|일주(?=일|년|간|마다)")


def check_leak(text: str) -> list[str]:
    hits = [w for w in LEAK_BANNED_HANJA if w in text]
    masked = _FALSE_POSITIVE.sub("○○○", text)  # 알려진 오탐 패턴 가림
    hits += [w for w in LEAK_BANNED_KO if w in masked]
    return hits


def render_user_section(idx: int, user, slot_keys: dict, cells: dict) -> str:
    ss = slot_keys["sipseong"]
    br = slot_keys["branch_rel"]
    total = slot_keys["total_score"]

    lines = []
    lines.append(f"## §{idx}. {user.name} ({user.id})")
    lines.append("")
    lines.append(f"- **일주**: {user.day_stem}{user.day_branch} ({user.note})")
    lines.append(f"- **오늘 일진**: {TODAY_STEM}{TODAY_BRANCH}")
    lines.append(f"- **십성**: {ss} · **지지관계**: {br}")
    lines.append(f"- **총점**: {total} ({MOOD3_KR[slot_keys['total_mood']]})")
    lines.append("")
    lines.append(f"### 헤드라인 (A)")
    lines.append(f"> {cells['A']}")
    lines.append("")

    # 시간대 (B/C)
    lines.append("### 시간대 흐름 (B+C)")
    lines.append("")
    lines.append("| 시간대 | 점수 | 분위기 (B) | 액션 (C) |")
    lines.append("|---|---|---|---|")
    for ts in TIME_SLOTS:
        s = score_time(ss, ts)
        lines.append(f"| {TIME_KOREAN[ts]} | {s} | {cells[f'B_{ts}']} | {cells[f'C_{ts}']} |")
    lines.append("")

    # 영역 (D/E/F/G)
    lines.append("### 영역별 (D/E/F/G)")
    lines.append("")
    for area in AREAS:
        s = score_area(ss, area)
        lines.append(f"#### {AREA_KOREAN[area]} ({s}점)")
        lines.append("")
        lines.append(f"**헤드 (D)**: {cells[f'D_{area}']}")
        lines.append("")
        lines.append(f"**관찰 卜 (E)**:")
        lines.append(f"> {cells[f'E_{area}']}")
        lines.append("")
        lines.append(f"**경계 警 (F)**:")
        lines.append(f"> {cells[f'F_{area}']}")
        lines.append("")
        lines.append(f"**조언 助 (G)**:")
        lines.append(f"> {cells[f'G_{area}']}")
        lines.append("")
    lines.append("---")
    return "\n".join(lines)


def render_diversity_table(all_results: list[tuple[object, dict, dict]]) -> str:
    """슬롯별로 10명 출력을 나란히 놓기 — 균질화 검사용."""
    lines = ["## §11. 슬롯별 다양성 검사 (10명 출력 나열)", ""]

    # A 헤드라인 — 10명
    lines.append("### 슬롯 A — 헤드라인 10개")
    lines.append("")
    for user, _, cells in all_results:
        lines.append(f"- **{user.name}**: {cells['A']}")
    lines.append("")

    # E/F/G — 영역별 10명 (love 한 영역만 샘플)
    for slot_key, slot_name in [("E", "卜 관찰"), ("F", "警 경계"), ("G", "助 조언")]:
        for area in AREAS:
            lines.append(f"### 슬롯 {slot_key} ({slot_name}) — {AREA_KOREAN[area]} 10명")
            lines.append("")
            for user, _, cells in all_results:
                txt = cells[f"{slot_key}_{area}"].replace("\n", " ")
                lines.append(f"- **{user.name}**: {txt}")
            lines.append("")

    lines.append("---")
    return "\n".join(lines)


def render_leak_table(all_results: list[tuple[object, dict, dict]]) -> str:
    lines = ["## §12. 도메인 용어 누출 검증", ""]
    lines.append("2단계 출력에서 금지어가 발견되면 ❌. 모두 ✅ 이어야 함.")
    lines.append("")
    lines.append("| 사용자 | 슬롯 | 누출 단어 |")
    lines.append("|---|---|---|")
    any_leak = False
    for user, _, cells in all_results:
        for label, text in cells.items():
            leaks = check_leak(text)
            if leaks:
                any_leak = True
                lines.append(f"| {user.name} | {label} | {', '.join(leaks)} |")
    if not any_leak:
        lines.append("| — | — | (누출 없음 ✅) |")
    lines.append("")
    return "\n".join(lines)


def render_pilot_doc(all_results: list[tuple[object, dict, dict]], stats: dict, output_path: Path) -> None:
    lines = []
    lines.append("# 깨비 무료사주 — 100칸 매트릭스 파일럿 결과")
    lines.append("")
    lines.append(f"- **오늘 (mock 일진)**: {TODAY_DISPLAY} / {TODAY_STEM}{TODAY_BRANCH}")
    lines.append(f"- **모델**: claude -p subprocess (Pro 구독)")
    lines.append(f"- **사용자 케이스**: 10명")
    lines.append("")

    # §0 통계
    lines.append("## §0. 실행 통계")
    lines.append("")
    lines.append(f"- 총 API 호출: **{stats['calls']}회**")
    lines.append(f"- 캐시 적중: {stats['cache_hits']}회")
    lines.append(f"- 누적 호출 시간: {stats['total_seconds']:.1f}초")
    lines.append(f"- 비용: **0원 (Pro 구독)**")
    lines.append("")

    # §1~10 사용자
    for i, (user, slot_keys, cells) in enumerate(all_results, start=1):
        lines.append(render_user_section(i, user, slot_keys, cells))
        lines.append("")

    # §11 다양성
    lines.append(render_diversity_table(all_results))
    lines.append("")

    # §12 누출
    lines.append(render_leak_table(all_results))

    output_path.write_text("\n".join(lines), encoding="utf-8")
