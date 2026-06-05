/**
 * 진태양시(眞太陽時) 경도 보정 회귀 테스트.
 *
 * 2026-06-02 결정: 표준시(HM-BE-28, commit bbf13d0)에서 진태양시로 복원.
 * getAdjustedBirthInstantForSaju가 출생 벽시계 시각에 경도 보정(분)을 적용해야 한다.
 * 이 테스트는 보정이 다시 폐기되면(표준시로 회귀) 즉시 실패한다 = 의도 가드.
 */

import {
  getAdjustedBirthInstantForSaju,
  parseBirthDateTimeKorea,
} from '../src/utils/date.js';
import { getLongitudeOffsetMinutesForSaju } from '../src/data/longitude_table.js';

const MIN = 60 * 1000;

function offsetMinutes(date: string, time: string, city?: string): number {
  const wall = parseBirthDateTimeKorea(date, time).getTime();
  const adjusted = getAdjustedBirthInstantForSaju(date, time, city).getTime();
  return (adjusted - wall) / MIN; // 음수 = 표준시보다 이른 시각(서쪽 경도)
}

describe('진태양시 경도 보정 (getAdjustedBirthInstantForSaju)', () => {
  test('서울 기준(미입력)은 표준시 대비 −32분', () => {
    expect(getLongitudeOffsetMinutesForSaju(undefined)).toBe(-32);
    expect(offsetMinutes('1992-11-14', '12:00')).toBe(-32);
  });

  test('미등록 도시도 서울 기준(−32분)으로 폴백', () => {
    expect(offsetMinutes('1992-11-14', '12:00', '없는도시999')).toBe(-32);
  });

  test('도시별 경도 보정 적용 — 부산 −24분', () => {
    expect(offsetMinutes('1992-11-14', '12:00', '부산')).toBe(-24);
  });

  test('보정이 실제로 적용된다(표준시와 동일하지 않음) — 회귀 가드', () => {
    const wall = parseBirthDateTimeKorea('1992-11-14', '12:00').getTime();
    const adjusted = getAdjustedBirthInstantForSaju('1992-11-14', '12:00').getTime();
    expect(adjusted).not.toBe(wall);
    expect(adjusted).toBeLessThan(wall); // 서쪽 경도 → 이른 시각
  });
});
