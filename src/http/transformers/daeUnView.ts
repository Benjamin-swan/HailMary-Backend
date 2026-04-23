/**
 * 대운(大運) 뷰.
 * `src/lib/dae_un.ts` 의 `DaeUnPeriod[]` 를 노출용 DTO 배열로 변환한다.
 *
 * 규칙:
 *   - 상위 7구간 고정 노출 (경쟁사 규격). 내부 배열이 7 미만이면 있는 만큼만.
 *   - startYear: 출생년 + startAge (간이 근사; 실제 절기 기준 생일 미경과는 고려하지 않음).
 *   - direction: 양년남/음년녀 = forward, 음년남/양년녀 = reverse.
 */

import type { SajuData, HeavenlyStem, EarthlyBranch } from '../../types/index.js';
import type { DaeUnPeriod } from '../../lib/dae_un.js';
import { hueFor } from './hueMap.js';

export interface DaeUnPeriodView {
  age: number;
  startYear: number;
  stem: HeavenlyStem;
  branch: EarthlyBranch;
  stemHanja: string;
  branchHanja: string;
  element: string;
  hue: string;
}

export type DaeUnDirection = 'forward' | 'reverse';

export interface DaeUnView {
  startAge: number;
  direction: DaeUnDirection;
  periods: DaeUnPeriodView[];
}

const STEM_HANJA: Record<HeavenlyStem, string> = {
  갑: '甲',
  을: '乙',
  병: '丙',
  정: '丁',
  무: '戊',
  기: '己',
  경: '庚',
  신: '辛',
  임: '壬',
  계: '癸',
};

const BRANCH_HANJA: Record<EarthlyBranch, string> = {
  자: '子',
  축: '丑',
  인: '寅',
  묘: '卯',
  진: '辰',
  사: '巳',
  오: '午',
  미: '未',
  신: '申',
  유: '酉',
  술: '戌',
  해: '亥',
};

const EXPOSED_COUNT = 7;

function directionOf(saju: SajuData): DaeUnDirection {
  const yin = saju.year.yinYang;
  if ((yin === '양' && saju.gender === 'male') || (yin === '음' && saju.gender === 'female')) {
    return 'forward';
  }
  return 'reverse';
}

function birthYearOf(saju: SajuData): number {
  // birthDate: 'YYYY-MM-DD'
  return Number.parseInt(saju.birthDate.slice(0, 4), 10);
}

export function toDaeUnView(saju: SajuData, periods: DaeUnPeriod[]): DaeUnView {
  const direction = directionOf(saju);
  const birthYear = birthYearOf(saju);
  const sliced = periods.slice(0, EXPOSED_COUNT);
  const startAge = sliced[0]?.startAge ?? 0;

  const views: DaeUnPeriodView[] = sliced.map((p) => ({
    age: p.startAge,
    startYear: birthYear + p.startAge,
    stem: p.stem,
    branch: p.branch,
    stemHanja: STEM_HANJA[p.stem],
    branchHanja: BRANCH_HANJA[p.branch],
    element: `${p.stemElement} / ${p.branchElement}`,
    hue: hueFor(p.stemElement),
  }));

  return {
    startAge,
    direction,
    periods: views,
  };
}
