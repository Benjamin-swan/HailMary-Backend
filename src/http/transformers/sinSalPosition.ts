/**
 * 연애운 포커스 신살 하이라이트 결정.
 *
 * 배경: `SajuData.sinSals` 는 위치 정보 없는 enum 배열이다. 프론트 응답의
 * `highlight` 는 "살명(한자) — 위치(한자)에 위치" 포맷이 필요하므로, 판정 로직을
 * 역참조해 어느 기둥에 해당 신살 글자가 놓였는지를 재계산한다.
 *
 * `src/lib/sin_sal.ts` 의 파이프라인은 수정하지 않고 read-only 로 참고한다.
 */

import type { SajuData, EarthlyBranch, SinSal } from '../../types/index.js';

export interface HighlightResult {
  text: string;
}

type PillarLabel = '년지' | '월지' | '일지' | '시지';

/**
 * 삼합 그룹별 도화/화개 대응 지지.
 * 도화: 해당 그룹의 "도화살" 대응 지지 (정통 기준).
 * 화개: 해당 그룹의 "화개살" 대응 지지.
 */
const THREE_HARMONY_GROUPS: ReadonlyArray<{
  set: ReadonlySet<EarthlyBranch>;
  doHwa: EarthlyBranch;
  hwaGae: EarthlyBranch;
}> = [
  { set: new Set<EarthlyBranch>(['인', '오', '술']), doHwa: '묘', hwaGae: '술' },
  { set: new Set<EarthlyBranch>(['사', '유', '축']), doHwa: '오', hwaGae: '축' },
  { set: new Set<EarthlyBranch>(['신', '자', '진']), doHwa: '유', hwaGae: '진' },
  { set: new Set<EarthlyBranch>(['해', '묘', '미']), doHwa: '자', hwaGae: '미' },
];

const LABEL_HANJA: Record<PillarLabel, string> = {
  년지: '年支',
  월지: '月支',
  일지: '日支',
  시지: '時支',
};

/**
 * 신살명(한자) 표기.
 */
const SIN_SAL_KOREAN_HANJA: Partial<Record<SinSal, string>> = {
  do_hwa_sal: '도화살(桃花殺)',
  hwa_gae_sal: '화개살(華蓋殺)',
};

/**
 * 기둥 → 지지 매핑. 일지 우선순위.
 * 시간이 unknown 이면 시지는 후보에서 제외한다.
 */
function collectBranches(
  saju: SajuData,
  excludeHour: boolean
): Array<{ label: PillarLabel; branch: EarthlyBranch }> {
  const list: Array<{ label: PillarLabel; branch: EarthlyBranch }> = [
    { label: '일지', branch: saju.day.branch },
    { label: '월지', branch: saju.month.branch },
    { label: '년지', branch: saju.year.branch },
  ];
  if (!excludeHour) {
    list.push({ label: '시지', branch: saju.hour.branch });
  }
  return list;
}

/**
 * 주어진 글자가 4기둥(시지 제외 가능) 중 어느 지지에 위치하는지 찾는다.
 * 일지 > 월지 > 년지 > 시지 순서.
 */
function locateBranch(
  pillars: Array<{ label: PillarLabel; branch: EarthlyBranch }>,
  target: EarthlyBranch
): PillarLabel | null {
  const hit = pillars.find((p) => p.branch === target);
  return hit ? hit.label : null;
}

/**
 * 도화살 위치 결정.
 */
function locateDoHwa(saju: SajuData, excludeHour: boolean): PillarLabel | null {
  const pillars = collectBranches(saju, excludeHour);
  const present = new Set(pillars.map((p) => p.branch));
  for (const group of THREE_HARMONY_GROUPS) {
    const groupPresent = [...group.set].some((b) => present.has(b));
    if (!groupPresent) continue;
    const pos = locateBranch(pillars, group.doHwa);
    if (pos) return pos;
  }
  return null;
}

/**
 * 화개살 위치 결정 (도화 부재 시 대체 하이라이트).
 */
function locateHwaGae(saju: SajuData, excludeHour: boolean): PillarLabel | null {
  const pillars = collectBranches(saju, excludeHour);
  const present = new Set(pillars.map((p) => p.branch));
  for (const group of THREE_HARMONY_GROUPS) {
    const groupPresent = [...group.set].some((b) => present.has(b));
    if (!groupPresent) continue;
    const pos = locateBranch(pillars, group.hwaGae);
    if (pos) return pos;
  }
  return null;
}

/**
 * 연애운 포커스 하이라이트를 결정한다.
 * 우선순위: 도화살 > 화개살 > 기본 문구.
 */
export function resolveHighlight(saju: SajuData, timeUnknown: boolean): HighlightResult {
  const sinSalList = saju.sinSals ?? [];
  const has = (s: SinSal) => sinSalList.includes(s);

  if (has('do_hwa_sal')) {
    const pos = locateDoHwa(saju, timeUnknown);
    if (pos) {
      return {
        text: `${SIN_SAL_KOREAN_HANJA.do_hwa_sal} — ${LABEL_HANJA[pos]}에 위치`,
      };
    }
  }

  if (has('hwa_gae_sal')) {
    const pos = locateHwaGae(saju, timeUnknown);
    if (pos) {
      return {
        text: `${SIN_SAL_KOREAN_HANJA.hwa_gae_sal} — ${LABEL_HANJA[pos]}에 위치`,
      };
    }
  }

  return { text: '명식의 흐름 — 담백한 결' };
}
