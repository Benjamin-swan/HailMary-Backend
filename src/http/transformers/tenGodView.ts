/**
 * 기둥별 십성(十星) 뷰.
 * - 천간 십성: 일간 대비 해당 기둥 천간의 십성.
 * - 지지 십성: 해당 기둥 지지의 정기(正氣) 지장간을 대표 천간으로 삼아 계산.
 *
 * 일주(日柱)의 천간은 규칙상 자기 자신(비견)으로 노출한다.
 */

import type { HeavenlyStem, EarthlyBranch, TenGod } from '../../types/index.js';
import { calculateTenGod, TEN_GODS_DATA } from '../../lib/ten_gods.js';

export interface TenGodView {
  heaven: string;
  earth: string;
  heavenHanja: string;
  earthHanja: string;
}

/**
 * 지지 → 정기(正氣) 대표 천간 매핑 (간이 룩업).
 * 지장간 정보가 제공되지 않는 경우의 폴백.
 */
const BRANCH_PRIMARY_STEM: Record<EarthlyBranch, HeavenlyStem> = {
  자: '계',
  축: '기',
  인: '갑',
  묘: '을',
  진: '무',
  사: '병',
  오: '정',
  미: '기',
  신: '경',
  유: '신',
  술: '무',
  해: '임',
};

function labelOf(tenGod: TenGod): { name: string; hanja: string } {
  const data = TEN_GODS_DATA[tenGod];
  return { name: data.name, hanja: data.hanja };
}

export function computeTenGodForStem(dayStem: HeavenlyStem, stem: HeavenlyStem): TenGod {
  return calculateTenGod(dayStem, stem);
}

export function computeTenGodForBranch(
  dayStem: HeavenlyStem,
  branch: EarthlyBranch,
  branchPrimaryStem?: HeavenlyStem
): TenGod {
  const stem = branchPrimaryStem ?? BRANCH_PRIMARY_STEM[branch];
  return calculateTenGod(dayStem, stem);
}

export function toTenGodView(args: {
  dayStem: HeavenlyStem;
  pillarStem: HeavenlyStem;
  pillarBranch: EarthlyBranch;
  branchPrimaryStem?: HeavenlyStem;
}): TenGodView {
  const heavenGod = computeTenGodForStem(args.dayStem, args.pillarStem);
  const earthGod = computeTenGodForBranch(args.dayStem, args.pillarBranch, args.branchPrimaryStem);
  const heavenLabel = labelOf(heavenGod);
  const earthLabel = labelOf(earthGod);
  return {
    heaven: heavenLabel.name,
    heavenHanja: heavenLabel.hanja,
    earth: earthLabel.name,
    earthHanja: earthLabel.hanja,
  };
}
