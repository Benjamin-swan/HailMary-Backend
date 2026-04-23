/**
 * 오행 → hex hue 고정 맵.
 * 프론트 디자인 토큰과 동기화된 값 (`dohwa_frontend/docs/backend-integration.md` §2).
 * 프론트 `mockSaju.ts` 는 수(水)가 `#A5BBD9` 였으나 계약서에서 `#6B8BB5` 로 최종 확정되었음.
 */

import type { WuXing } from '../../types/index.js';

export const HUE_MAP: Record<WuXing, string> = {
  목: '#9CC8B0',
  화: '#E6A88E',
  토: '#E6C58E',
  금: '#C5CAD4',
  수: '#6B8BB5',
};

export function hueFor(element: WuXing): string {
  return HUE_MAP[element];
}
