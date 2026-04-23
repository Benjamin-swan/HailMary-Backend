/**
 * 십이운성(十二運星) 계산 모듈.
 * 일간(day stem)을 기준으로 각 지지의 십이운성 단계를 결정한다.
 *
 * `src/data/twelve_phases_table.ts` 의 룩업 테이블을 사용하는 얇은 래퍼.
 */

import type { HeavenlyStem, EarthlyBranch } from '../types/index.js';
import {
  TWELVE_PHASES_TABLE,
  TWELVE_PHASE_LABEL,
  type TwelvePhase,
} from '../data/twelve_phases_table.js';

export type { TwelvePhase } from '../data/twelve_phases_table.js';
export { TWELVE_PHASE_LABEL } from '../data/twelve_phases_table.js';

/**
 * 일간 + 지지 → 12운성 단계.
 */
export function getTwelvePhase(dayStem: HeavenlyStem, branch: EarthlyBranch): TwelvePhase {
  return TWELVE_PHASES_TABLE[dayStem][branch];
}

/**
 * 라벨(한글·한자) 반환.
 */
export function getTwelvePhaseLabel(phase: TwelvePhase): { name: string; hanja: string } {
  return TWELVE_PHASE_LABEL[phase];
}
