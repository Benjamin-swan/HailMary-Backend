/**
 * /api/saju/free 라우트 통합 테스트.
 * - Hono 앱의 `fetch` 를 직접 호출해 supertest 같은 추가 의존성 없이 테스트.
 * - calculateSaju / saveSajuRequest / newRequestId 는 DI 스텁으로 대체 → DB 불필요.
 */

import { describe, it, expect, jest } from '@jest/globals';
import { Hono } from 'hono';
import type { SajuData } from '../../src/types/index.js';
import type { DaeUnPeriod } from '../../src/lib/dae_un.js';
import { createFreeSajuRoute, type FreeSajuDeps } from '../../src/http/routes/freeSaju.js';

function fakeSaju(): SajuData {
  return {
    birthDate: '1998-03-15',
    birthTime: '14:30',
    birthCity: '서울',
    calendar: 'solar',
    isLeapMonth: false,
    gender: 'female',
    year: { stem: '무', branch: '인', stemElement: '토', branchElement: '목', yinYang: '양' },
    month: { stem: '을', branch: '묘', stemElement: '목', branchElement: '목', yinYang: '음' },
    day: { stem: '갑', branch: '오', stemElement: '목', branchElement: '화', yinYang: '양' },
    hour: { stem: '신', branch: '미', stemElement: '금', branchElement: '토', yinYang: '음' },
    wuxingCount: { 목: 3, 화: 1, 토: 2, 금: 1, 수: 0 },
    tenGods: [],
    sinSals: ['do_hwa_sal'],
    dayMasterStrength: { level: 'medium', score: 50, analysis: '' },
    yongSin: { primaryYongSin: '수', reasoning: 'internal-reasoning' },
  };
}

function fakeDaeUn(): DaeUnPeriod[] {
  return Array.from({ length: 8 }, (_, i) => ({
    startAge: 2 + i * 10,
    endAge: 11 + i * 10,
    stem: '갑',
    branch: '오',
    stemElement: '목' as const,
    branchElement: '화' as const,
    pillarIndex: i,
  }));
}

function buildApp(overrides: Partial<FreeSajuDeps> = {}) {
  const saveSpy = jest.fn(async () => {});
  const deps: FreeSajuDeps = {
    calculateSaju: () => fakeSaju(),
    calculateDaeUn: () => fakeDaeUn(),
    saveSajuRequest: saveSpy as unknown as FreeSajuDeps['saveSajuRequest'],
    newRequestId: () => 'svr_FIXED',
    ...overrides,
  };
  const app = new Hono();
  app.route('/api/saju/free', createFreeSajuRoute(deps));
  return { app, saveSpy };
}

async function post(app: Hono, body: unknown): Promise<Response> {
  return app.fetch(
    new Request('http://localhost/api/saju/free', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  );
}

describe('POST /api/saju/free', () => {
  it('정상 요청 → 200 + pillars 길이 4 + sajuRequestId', async () => {
    const { app, saveSpy } = buildApp();
    const res = await post(app, {
      birth: '1998-03-15',
      calendar: 'solar',
      time: '14:30',
      gender: 'female',
    });

    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      pillars: Array<{ unknown: boolean; label: string }>;
      highlight: string;
      sajuRequestId: string;
    };
    expect(body.pillars).toHaveLength(4);
    expect(body.pillars.every((p) => p.unknown === false)).toBe(true);
    expect(body.sajuRequestId).toBe('svr_FIXED');
    expect(saveSpy).toHaveBeenCalledTimes(1);
  });

  it('time unknown → 시주는 placeholder, 나머지 정상', async () => {
    const { app } = buildApp();
    const res = await post(app, {
      birth: '1998-03-15',
      calendar: 'solar',
      time: 'unknown',
      gender: 'female',
    });

    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      pillars: Array<{ label: string; unknown: boolean; heaven: string }>;
    };
    expect(body.pillars).toHaveLength(4);
    expect(body.pillars[3]!.unknown).toBe(true);
    expect(body.pillars[3]!.heaven).toBe('?');
    expect(body.pillars.slice(0, 3).every((p) => p.unknown === false)).toBe(true);
  });

  it('birth 포맷이 YYYY-MM-DD 아니면 400', async () => {
    const { app, saveSpy } = buildApp();
    const res = await post(app, {
      birth: '1998.03.15',
      calendar: 'solar',
      time: '14:30',
      gender: 'female',
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as { error: string };
    expect(body.error).toBe('BAD_REQUEST');
    expect(saveSpy).not.toHaveBeenCalled();
  });

  it('연도 범위 초과(1899, 2201) → 400', async () => {
    const { app } = buildApp();
    for (const birth of ['1899-12-31', '2201-01-01']) {
      const res = await post(app, { birth, calendar: 'solar', time: '14:30', gender: 'female' });
      expect(res.status).toBe(400);
    }
  });

  it('time 포맷 오류 → 400', async () => {
    const { app } = buildApp();
    const res = await post(app, {
      birth: '1998-03-15',
      calendar: 'solar',
      time: '14시',
      gender: 'female',
    });
    expect(res.status).toBe(400);
  });

  it('gender 누락 → 400', async () => {
    const { app } = buildApp();
    const res = await post(app, { birth: '1998-03-15', calendar: 'solar', time: '14:30' });
    expect(res.status).toBe(400);
  });

  it('계산기 예외 → 500 CALCULATION_FAILED, 스택 노출 금지', async () => {
    const { app, saveSpy } = buildApp({
      calculateSaju: () => {
        throw new Error('internal boom with secret details');
      },
    });
    const res = await post(app, {
      birth: '1998-03-15',
      calendar: 'solar',
      time: '14:30',
      gender: 'female',
    });
    expect(res.status).toBe(500);
    const text = await res.text();
    expect(text).toContain('CALCULATION_FAILED');
    expect(text).not.toContain('secret details');
    expect(saveSpy).not.toHaveBeenCalled();
  });

  it('응답에 영업 비밀 필드 문자열 부재 (확장 정책 기준)', async () => {
    const { app } = buildApp();
    const res = await post(app, {
      birth: '1998-03-15',
      calendar: 'solar',
      time: '14:30',
      gender: 'female',
    });
    const text = await res.text();
    // 내부 원본 필드명 · 근거 텍스트는 계속 차단
    for (const key of [
      'wuxingCount',
      'jiJangGan',
      'tenGodsDistribution',
      'dayMasterStrength',
      'gyeokGuk',
      'branchRelations',
      'wolRyeong',
      'reasoning',
      'analysis',
      'specialMarks',
      'dominantElements',
      'weakElements',
      'stemElement',
      'branchElement',
      'internal-reasoning',
    ]) {
      expect(text).not.toContain(key);
    }
  });
});
