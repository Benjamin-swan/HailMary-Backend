/**
 * POST /api/saju/free
 * 무료 사주 계산 엔드포인트.
 *
 * 플로:
 *   1) Zod 검증 (실패 → 400 BAD_REQUEST)
 *   2) time === 'unknown' 시 내부 계산엔 12:00 주입, 시주는 응답에서 placeholder 처리
 *   3) calculateSaju 호출 (lib/saju.ts, 수정 금지)
 *   4) sajuRequestId 발급 → SajuRequest 영속화
 *   5) sajuDisplay 트랜스포머로 영업 비밀 필드 제거한 응답 반환
 *   6) 전역 catch → 500 CALCULATION_FAILED (내부 에러는 서버 로그에만)
 *
 * 의존성 주입: 테스트에서 saju 계산기/저장소/ID 발급기를 stub 으로 대체 가능.
 */

import { Hono } from 'hono';
import type { SajuData, CalendarType, Gender } from '../../types/index.js';
import type { DaeUnPeriod } from '../../lib/dae_un.js';
import { freeSajuRequestSchema } from '../schemas/freeSaju.js';
import { buildFreeSajuResponse } from '../transformers/sajuDisplay.js';
import { badRequest, calculationFailed } from '../errors.js';

const DEFAULT_BIRTH_CITY = '서울';
const FALLBACK_TIME_FOR_UNKNOWN = '12:00';

export interface FreeSajuDeps {
  calculateSaju: (
    birthDate: string,
    birthTime: string,
    calendar: CalendarType,
    isLeapMonth: boolean,
    gender: Gender,
    birthCity?: string
  ) => SajuData;
  calculateDaeUn: (saju: SajuData) => DaeUnPeriod[];
  saveSajuRequest: (args: {
    id: string;
    birth: string;
    birthTime: string | null;
    calendar: CalendarType;
    gender: Gender;
    birthCity: string;
    sajuData: SajuData;
  }) => Promise<void>;
  newRequestId: () => string;
}

export function createFreeSajuRoute(deps: FreeSajuDeps): Hono {
  const route = new Hono();

  route.post('/', async (c) => {
    let body: unknown;
    try {
      body = await c.req.json();
    } catch {
      return c.json(badRequest([{ path: [], message: 'invalid JSON body' }]), 400);
    }

    const parsed = freeSajuRequestSchema.safeParse(body);
    if (!parsed.success) {
      return c.json(badRequest(parsed.error.issues), 400);
    }

    const { birth, calendar, time, gender } = parsed.data;
    const timeUnknown = time === 'unknown';
    const birthTimeForCalc = timeUnknown ? FALLBACK_TIME_FOR_UNKNOWN : time;

    try {
      const saju = deps.calculateSaju(
        birth,
        birthTimeForCalc,
        calendar,
        false,
        gender,
        DEFAULT_BIRTH_CITY
      );
      const daeUnPeriods = deps.calculateDaeUn(saju);
      const sajuRequestId = deps.newRequestId();

      await deps.saveSajuRequest({
        id: sajuRequestId,
        birth,
        birthTime: timeUnknown ? null : time,
        calendar,
        gender,
        birthCity: DEFAULT_BIRTH_CITY,
        sajuData: saju,
      });

      const response = buildFreeSajuResponse({
        saju,
        daeUnPeriods,
        sajuRequestId,
        timeUnknown,
      });
      return c.json(response, 200);
    } catch (err) {
      console.error('[freeSaju] calculation/persistence failed', err);
      return c.json(calculationFailed(), 500);
    }
  });

  return route;
}
