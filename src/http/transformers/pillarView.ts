/**
 * Pillar(도메인) → PillarView(응답) 변환.
 *
 * 응답 필드:
 *   - heaven/earth: 한자 1자 (천간/지지)
 *   - heavenHangul/earthHangul: 한글 1자
 *   - element: "천간오행 / 지지오행" (한글)
 *   - hue: 천간 오행 기준 hex
 *   - yinYang: { heaven, earth } 기둥 음양
 *   - tenGod: 천간·지지 십성 (한글 + 한자)
 *   - twelvePhase: 십이운성 단계 (한글 + 한자)
 *   - sinSals: 이 기둥 지지에 놓인 신살 목록
 *   - unknown: 시주가 계산 불가한 경우만 true
 *
 * 영업 비밀 보호: `Pillar.stemElement`/`branchElement`/`yinYang` 원본 enum 은
 * 그대로 노출하지 않고 표시용 포맷으로만 가공한다.
 */

import type { Pillar, HeavenlyStem, EarthlyBranch, YinYang } from '../../types/index.js';
import { hueFor } from './hueMap.js';
import type { TenGodView } from './tenGodView.js';
import type { SinSalEntry } from './pillarSinSals.js';
import type { TwelvePhase } from '../../data/twelve_phases_table.js';
import { getTwelvePhaseLabel } from '../../lib/twelve_phases.js';

export interface PillarView {
  label: '년주' | '월주' | '일주' | '시주';
  heaven: string;
  earth: string;
  heavenHangul: string;
  earthHangul: string;
  element: string;
  hue: string;
  yinYang: { heaven: YinYang; earth: YinYang };
  tenGod: TenGodView;
  twelvePhase: { name: string; hanja: string };
  sinSals: SinSalEntry[];
  unknown: boolean;
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

/**
 * 지지 음양. 전통 사주 기준 (자·인·진·오·신·술=양, 축·묘·사·미·유·해=음).
 */
const BRANCH_YIN_YANG: Record<EarthlyBranch, YinYang> = {
  자: '양',
  축: '음',
  인: '양',
  묘: '음',
  진: '양',
  사: '음',
  오: '양',
  미: '음',
  신: '양',
  유: '음',
  술: '양',
  해: '음',
};

export interface ToPillarViewArgs {
  label: PillarView['label'];
  pillar: Pillar;
  tenGod: TenGodView;
  twelvePhase: TwelvePhase;
  sinSals: SinSalEntry[];
}

export function toPillarView({
  label,
  pillar,
  tenGod,
  twelvePhase,
  sinSals,
}: ToPillarViewArgs): PillarView {
  const phaseLabel = getTwelvePhaseLabel(twelvePhase);
  return {
    label,
    heaven: STEM_HANJA[pillar.stem],
    earth: BRANCH_HANJA[pillar.branch],
    heavenHangul: pillar.stem,
    earthHangul: pillar.branch,
    element: `${pillar.stemElement} / ${pillar.branchElement}`,
    hue: hueFor(pillar.stemElement),
    yinYang: {
      heaven: pillar.yinYang,
      earth: BRANCH_YIN_YANG[pillar.branch],
    },
    tenGod,
    twelvePhase: phaseLabel,
    sinSals,
    unknown: false,
  };
}

export function unknownHourPillar(): PillarView {
  return {
    label: '시주',
    heaven: '?',
    earth: '?',
    heavenHangul: '?',
    earthHangul: '?',
    element: '—',
    hue: '—',
    yinYang: { heaven: '양', earth: '양' },
    tenGod: { heaven: '—', earth: '—', heavenHanja: '—', earthHanja: '—' },
    twelvePhase: { name: '—', hanja: '—' },
    sinSals: [],
    unknown: true,
  };
}
