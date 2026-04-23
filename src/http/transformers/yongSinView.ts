/**
 * 용신(用神) 뷰: primary(용신) / secondary(희신) / opposing(기신).
 *
 * 기신(忌神) = 용신이 극(剋)하는 오행 (오행 상극 관계 역산).
 *   예) 용신 수 → 기신 화 (수극화)
 *
 * 영업 비밀: 내부 `yongSin.reasoning` 은 노출하지 않는다.
 */

import type { WuXing, SajuData } from '../../types/index.js';
import { WUXING_DATA, WUXING_DESTRUCTION } from '../../data/wuxing.js';

export type YongSinRole = '용신' | '희신' | '기신';

export interface YongSinSlot {
  element: WuXing;
  hanja: string;
  role: YongSinRole;
}

export interface YongSinView {
  primary: YongSinSlot;
  secondary: YongSinSlot | null;
  opposing: YongSinSlot;
}

function slot(element: WuXing, role: YongSinRole): YongSinSlot {
  return {
    element,
    hanja: WUXING_DATA[element].hanja,
    role,
  };
}

export function toYongSinView(saju: SajuData): YongSinView | null {
  const source = saju.yongSin;
  if (!source) return null;

  const primary = slot(source.primaryYongSin, '용신');
  const secondary = source.secondaryYongSin ? slot(source.secondaryYongSin, '희신') : null;
  const opposing = slot(WUXING_DESTRUCTION[source.primaryYongSin], '기신');

  return { primary, secondary, opposing };
}
