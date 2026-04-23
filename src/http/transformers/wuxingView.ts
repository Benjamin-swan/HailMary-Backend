/**
 * 오행 분포 뷰: counts, ratios(%), judgments.
 *
 * 판정 임계값 (개수 기반):
 *   0개 → 결핍
 *   1개 → 적정
 *   2개 → 발달
 *   3개 이상 → 과다
 *
 * ratios 는 소수 1자리까지 내려 총합이 100% 에 근접하도록 반올림한다.
 */

import type { WuXing } from '../../types/index.js';

export type WuxingJudgment = '결핍' | '적정' | '발달' | '과다';

export interface WuxingView {
  counts: Record<WuXing, number>;
  ratios: Record<WuXing, number>;
  judgments: Record<WuXing, WuxingJudgment>;
}

const WUXING_ORDER: ReadonlyArray<WuXing> = ['목', '화', '토', '금', '수'];

function judge(count: number): WuxingJudgment {
  if (count === 0) return '결핍';
  if (count === 1) return '적정';
  if (count === 2) return '발달';
  return '과다';
}

export function toWuxingView(counts: Record<WuXing, number>): WuxingView {
  const total = WUXING_ORDER.reduce((sum, el) => sum + (counts[el] ?? 0), 0);

  const ratios = {} as Record<WuXing, number>;
  const judgments = {} as Record<WuXing, WuxingJudgment>;
  const safeCounts = {} as Record<WuXing, number>;

  for (const el of WUXING_ORDER) {
    const count = counts[el] ?? 0;
    safeCounts[el] = count;
    const ratio = total === 0 ? 0 : (count / total) * 100;
    ratios[el] = Math.round(ratio * 10) / 10;
    judgments[el] = judge(count);
  }

  return {
    counts: safeCounts,
    ratios,
    judgments,
  };
}
