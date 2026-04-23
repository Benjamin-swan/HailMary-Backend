/**
 * SajuData(내부 전체) → 프론트 표시용 응답 객체.
 *
 * 응답 포함 (명리 표준 공개 필드):
 *   - pillars: 4기둥 (한자/한글/음양/오행/십성/십이운성/신살/hue)
 *   - highlight: 연애운 포커스 한 줄
 *   - wuxing: 오행 counts/ratios/judgments
 *   - yongSin: 용신/희신/기신
 *   - dayMaster: 일간 + 신강신약 7단계
 *   - daeUn: 대운 7구간 + 방향
 *   - sajuRequestId
 *
 * 영업 비밀 차단 (절대 노출 금지):
 *   - yongSin.reasoning, dayMasterStrength.score/analysis
 *   - gyeokGuk 세부, jiJangGan 세부, branchRelations 세부
 *   - wolRyeong (득령 근거), specialMarks
 */

import type { SajuData, HeavenlyStem, EarthlyBranch } from '../../types/index.js';
import { toPillarView, unknownHourPillar, type PillarView } from './pillarView.js';
import { resolveHighlight } from './sinSalPosition.js';
import { toWuxingView, type WuxingView } from './wuxingView.js';
import { toYongSinView, type YongSinView } from './yongSinView.js';
import { toDayMasterView, type DayMasterView } from './dayMasterView.js';
import { toDaeUnView, type DaeUnView } from './daeUnView.js';
import { placeSinSalsByPillar, type PillarKey } from './pillarSinSals.js';
import { toTenGodView } from './tenGodView.js';
import { getTwelvePhase } from '../../lib/twelve_phases.js';
import type { DaeUnPeriod } from '../../lib/dae_un.js';

export interface FreeSajuResponse {
  pillars: PillarView[];
  highlight: string;
  wuxing: WuxingView;
  yongSin: YongSinView | null;
  dayMaster: DayMasterView;
  daeUn: DaeUnView;
  sajuRequestId: string;
}

export interface BuildFreeSajuArgs {
  saju: SajuData;
  daeUnPeriods: DaeUnPeriod[];
  sajuRequestId: string;
  timeUnknown: boolean;
}

export function buildFreeSajuResponse({
  saju,
  daeUnPeriods,
  sajuRequestId,
  timeUnknown,
}: BuildFreeSajuArgs): FreeSajuResponse {
  const dayStem = saju.day.stem;
  const sinSalsByPillar = placeSinSalsByPillar(saju, timeUnknown);

  const yearView = toPillarView({
    label: '년주',
    pillar: saju.year,
    tenGod: toTenGodView({
      dayStem,
      pillarStem: saju.year.stem,
      pillarBranch: saju.year.branch,
      branchPrimaryStem: primaryStemOf(saju, 'year'),
    }),
    twelvePhase: getTwelvePhase(dayStem, saju.year.branch),
    sinSals: sinSalsByPillar.year,
  });

  const monthView = toPillarView({
    label: '월주',
    pillar: saju.month,
    tenGod: toTenGodView({
      dayStem,
      pillarStem: saju.month.stem,
      pillarBranch: saju.month.branch,
      branchPrimaryStem: primaryStemOf(saju, 'month'),
    }),
    twelvePhase: getTwelvePhase(dayStem, saju.month.branch),
    sinSals: sinSalsByPillar.month,
  });

  const dayView = toPillarView({
    label: '일주',
    pillar: saju.day,
    tenGod: toTenGodView({
      dayStem,
      pillarStem: saju.day.stem,
      pillarBranch: saju.day.branch,
      branchPrimaryStem: primaryStemOf(saju, 'day'),
    }),
    twelvePhase: getTwelvePhase(dayStem, saju.day.branch),
    sinSals: sinSalsByPillar.day,
  });

  const hourView = timeUnknown
    ? unknownHourPillar()
    : toPillarView({
        label: '시주',
        pillar: saju.hour,
        tenGod: toTenGodView({
          dayStem,
          pillarStem: saju.hour.stem,
          pillarBranch: saju.hour.branch,
          branchPrimaryStem: primaryStemOf(saju, 'hour'),
        }),
        twelvePhase: getTwelvePhase(dayStem, saju.hour.branch),
        sinSals: sinSalsByPillar.hour,
      });

  const highlight = resolveHighlight(saju, timeUnknown);

  return {
    pillars: [yearView, monthView, dayView, hourView],
    highlight: highlight.text,
    wuxing: toWuxingView(saju.wuxingCount),
    yongSin: toYongSinView(saju),
    dayMaster: toDayMasterView(saju),
    daeUn: toDaeUnView(saju, daeUnPeriods),
    sajuRequestId,
  };
}

function primaryStemOf(saju: SajuData, key: PillarKey): HeavenlyStem | undefined {
  return saju.jiJangGan?.[key]?.primary?.stem;
}

// 타입 재노출 (기존 import 경로 유지용).
export type { PillarView } from './pillarView.js';
// 하위 트랜스포머에서 EarthlyBranch 재사용이 필요할 수 있어 유지.
export type { EarthlyBranch };
