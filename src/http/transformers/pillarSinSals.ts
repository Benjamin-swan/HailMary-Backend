/**
 * 기둥별(년/월/일/시) 신살 배치 결정.
 *
 * `src/lib/sin_sal.ts` 의 `findSinSals` 는 위치 없는 enum 배열만 반환하므로,
 * 각 신살이 어떤 기둥(지지)에 위치하는지를 판정 규칙을 역참조해 재계산한다.
 *
 * `src/lib/sin_sal.ts` 의 계산 파이프라인은 수정하지 않고 read-only 로 참고.
 */

import type { SajuData, EarthlyBranch, HeavenlyStem, SinSal } from '../../types/index.js';
import { SIN_SAL_DATA } from '../../lib/sin_sal.js';

export type PillarKey = 'year' | 'month' | 'day' | 'hour';

export interface SinSalEntry {
  slug: SinSal;
  label: string;
  hanja: string;
}

const CHEON_EUL_TABLE: Record<HeavenlyStem, EarthlyBranch[]> = {
  갑: ['축', '미'],
  을: ['자', '신'],
  병: ['해', '유'],
  정: ['해', '유'],
  무: ['축', '미'],
  기: ['자', '신'],
  경: ['축', '미'],
  신: ['인', '오'],
  임: ['사', '묘'],
  계: ['사', '묘'],
};

/**
 * 삼합 그룹 → (도화·역마·화개) 대응 지지.
 * 그룹 내 지지 중 하나라도 4기둥에 존재해야 활성화.
 */
const THREE_HARMONY_GROUPS: ReadonlyArray<{
  set: ReadonlySet<EarthlyBranch>;
  doHwa: EarthlyBranch;
  yeokMa: EarthlyBranch;
  hwaGae: EarthlyBranch;
}> = [
  { set: new Set(['인', '오', '술']), doHwa: '묘', yeokMa: '신', hwaGae: '술' },
  { set: new Set(['사', '유', '축']), doHwa: '오', yeokMa: '해', hwaGae: '축' },
  { set: new Set(['신', '자', '진']), doHwa: '유', yeokMa: '인', hwaGae: '진' },
  { set: new Set(['해', '묘', '미']), doHwa: '자', yeokMa: '사', hwaGae: '미' },
];

/**
 * 일지 기준 공망 지지.
 */
const GONG_MANG_TABLE: Record<EarthlyBranch, EarthlyBranch[]> = {
  자: ['술', '해'],
  축: ['술', '해'],
  인: ['자', '축'],
  묘: ['자', '축'],
  진: ['인', '묘'],
  사: ['인', '묘'],
  오: ['진', '사'],
  미: ['진', '사'],
  신: ['오', '미'],
  유: ['오', '미'],
  술: ['신', '유'],
  해: ['신', '유'],
};

/**
 * 원진살 충(冲) 쌍.
 */
const CHUNG_PAIRS: ReadonlyArray<[EarthlyBranch, EarthlyBranch]> = [
  ['자', '오'],
  ['축', '미'],
  ['인', '신'],
  ['묘', '유'],
  ['진', '술'],
  ['사', '해'],
];

const GWI_MUN_BRANCHES: ReadonlySet<EarthlyBranch> = new Set(['인', '신', '사', '해']);

interface PillarRef {
  key: PillarKey;
  branch: EarthlyBranch;
}

function collectPillars(saju: SajuData, excludeHour: boolean): PillarRef[] {
  const list: PillarRef[] = [
    { key: 'year', branch: saju.year.branch },
    { key: 'month', branch: saju.month.branch },
    { key: 'day', branch: saju.day.branch },
  ];
  if (!excludeHour) {
    list.push({ key: 'hour', branch: saju.hour.branch });
  }
  return list;
}

function addTo(buckets: Record<PillarKey, SinSal[]>, key: PillarKey, slug: SinSal): void {
  if (!buckets[key].includes(slug)) {
    buckets[key].push(slug);
  }
}

function emptyBuckets(): Record<PillarKey, SinSal[]> {
  return { year: [], month: [], day: [], hour: [] };
}

/**
 * 삼합 기반 신살(도화·역마·화개)을 기둥별로 배치.
 */
function placeThreeHarmonyBased(
  pillars: PillarRef[],
  slug: 'do_hwa_sal' | 'yeok_ma_sal' | 'hwa_gae_sal',
  buckets: Record<PillarKey, SinSal[]>
): void {
  const present = new Set(pillars.map((p) => p.branch));
  for (const group of THREE_HARMONY_GROUPS) {
    const active = [...group.set].some((b) => present.has(b));
    if (!active) continue;
    const target =
      slug === 'do_hwa_sal' ? group.doHwa : slug === 'yeok_ma_sal' ? group.yeokMa : group.hwaGae;
    for (const p of pillars) {
      if (p.branch === target) {
        addTo(buckets, p.key, slug);
      }
    }
  }
}

/**
 * 신살 목록(enum 배열)을 기둥별 배치로 재계산한다.
 */
export function placeSinSalsByPillar(
  saju: SajuData,
  timeUnknown: boolean
): Record<PillarKey, SinSalEntry[]> {
  const pillars = collectPillars(saju, timeUnknown);
  const sinSals = saju.sinSals ?? [];
  const buckets = emptyBuckets();

  for (const slug of sinSals) {
    switch (slug) {
      case 'cheon_eul_gwi_in': {
        const targets = CHEON_EUL_TABLE[saju.day.stem];
        for (const p of pillars) {
          if (targets.includes(p.branch)) {
            addTo(buckets, p.key, slug);
          }
        }
        break;
      }
      case 'do_hwa_sal':
      case 'yeok_ma_sal':
      case 'hwa_gae_sal':
        placeThreeHarmonyBased(pillars, slug, buckets);
        break;
      case 'gong_mang': {
        const targets = GONG_MANG_TABLE[saju.day.branch];
        for (const p of pillars) {
          if (targets.includes(p.branch)) {
            addTo(buckets, p.key, slug);
          }
        }
        break;
      }
      case 'won_jin_sal': {
        for (const [a, b] of CHUNG_PAIRS) {
          const has = new Set(pillars.map((p) => p.branch));
          if (has.has(a) && has.has(b)) {
            for (const p of pillars) {
              if (p.branch === a || p.branch === b) {
                addTo(buckets, p.key, slug);
              }
            }
          }
        }
        break;
      }
      case 'gwi_mun_gwan_sal': {
        for (const p of pillars) {
          if (GWI_MUN_BRANCHES.has(p.branch)) {
            addTo(buckets, p.key, slug);
          }
        }
        break;
      }
      default:
        // 나머지 신살(천덕·월덕·문창·학당·금여록·양인·백호·고숙)은
        // 현재 findSinSals 가 생성하지 않으므로 배치 대상이 아니다.
        // 추후 findSinSals 확장 시 대응 케이스 추가.
        break;
    }
  }

  const result: Record<PillarKey, SinSalEntry[]> = {
    year: buckets.year.map(toEntry),
    month: buckets.month.map(toEntry),
    day: buckets.day.map(toEntry),
    hour: buckets.hour.map(toEntry),
  };
  return result;
}

function toEntry(slug: SinSal): SinSalEntry {
  const info = SIN_SAL_DATA[slug];
  return { slug, label: info.name, hanja: info.hanja };
}
