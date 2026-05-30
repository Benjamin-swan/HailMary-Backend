"""깨비 일일사주 캐시 키 빌더 (HM-BE-67).

설계:
- `kkebi:pillars:{birth}` — 추출된 일주(stem/branch) 튜플. 일주는 생년월일만으로 결정 → 시·성별 무관.
- `kkebi:result:{stem}{branch}:{date}` — 합성 결과(점수/lucky/본문/cycle). date 포함 → KST 자정 자동 전환.

KEY_VERSION 상수는 점수 룰 hot-fix 시 prefix bump로 전체 무효화 옵션 (현재는 v1 고정, FLUSHDB로도 충분).
"""
from __future__ import annotations

KEY_VERSION = "v1"


def kkebi_pillars_key(birth: str) -> str:
    """일주 추출 결과 캐시 키. birth = 'YYYY-MM-DD' 가정.

    일주는 생년월일만으로 결정되는 절대 달력 lookup이라 시/성별 무관.
    FortuneTeller 전체 응답이 아닌 stem/branch 튜플만 저장 (다른 도메인의 성별 의존 필드와 격리).
    """
    return f"kkebi:pillars:{KEY_VERSION}:{birth}"


def kkebi_result_key(user_stem: str, user_branch: str, kst_date_iso: str) -> str:
    """합성 결과 캐시 키. kst_date_iso = 'YYYY-MM-DD' KST 기준.

    date가 키에 포함되므로 자정 자동 전환 — 다음날 자동으로 새 키로 조회되어 miss → 새 합성.
    """
    return f"kkebi:result:{KEY_VERSION}:{user_stem}{user_branch}:{kst_date_iso}"
