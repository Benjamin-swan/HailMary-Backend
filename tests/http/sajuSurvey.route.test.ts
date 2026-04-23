/**
 * /api/saju/survey 라우트 통합 테스트.
 * - DI 스텁으로 DB 회피.
 * - 구조 검증(길이·개수·포맷) + 인가 경계(존재하지 않는 sajuRequestId) + 동시성 규칙(upsert) 검증.
 */

import { describe, it, expect, jest } from '@jest/globals';
import { Hono } from 'hono';
import {
  createSajuSurveyRoute,
  type SajuSurveyDeps,
  type SaveSurveyArgs,
} from '../../src/http/routes/sajuSurvey.js';

const VALID_SAJU_REQUEST_ID = 'svr_01KPQ7PKTCFXC9YR2RYW201TJX';

function buildApp(overrides: Partial<SajuSurveyDeps> = {}) {
  const upsertSpy = jest.fn(async (_args: SaveSurveyArgs) => {});
  const existsSpy = jest.fn(async (_id: string) => true);
  const deps: SajuSurveyDeps = {
    sajuRequestExists: existsSpy as unknown as SajuSurveyDeps['sajuRequestExists'],
    upsertSurvey: upsertSpy as unknown as SajuSurveyDeps['upsertSurvey'],
    newSurveyId: () => 'svy_FIXED',
    ...overrides,
  };
  const app = new Hono();
  app.route('/api/saju/survey', createSajuSurveyRoute(deps));
  return { app, upsertSpy, existsSpy };
}

async function post(app: Hono, body: unknown): Promise<Response> {
  return app.fetch(
    new Request('http://localhost/api/saju/survey', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  );
}

const baseBody = {
  sajuRequestId: VALID_SAJU_REQUEST_ID,
  surveyVersion: 'v1',
  step1: ['waiting_new', 'dating'],
  step2: ['destined', 'timing'],
  step3: '요즘 밤잠 설치는 고민',
};

describe('POST /api/saju/survey', () => {
  it('정상 요청 → 200 { ok:true }, upsert 1회 호출', async () => {
    const { app, upsertSpy } = buildApp();
    const res = await post(app, baseBody);

    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ ok: true });
    expect(upsertSpy).toHaveBeenCalledTimes(1);
    const call = upsertSpy.mock.calls[0]![0] as SaveSurveyArgs;
    expect(call.id).toBe('svy_FIXED');
    expect(call.sajuRequestId).toBe(VALID_SAJU_REQUEST_ID);
    expect(call.step3).toBe('요즘 밤잠 설치는 고민');
  });

  it('step3 생략 → step3=null 로 저장', async () => {
    const { app, upsertSpy } = buildApp();
    const { step3: _omit, ...noStep3 } = baseBody;
    const res = await post(app, noStep3);

    expect(res.status).toBe(200);
    const call = upsertSpy.mock.calls[0]![0] as SaveSurveyArgs;
    expect(call.step3).toBeNull();
  });

  it('step3 공백만 "   " → trim 후 null', async () => {
    const { app, upsertSpy } = buildApp();
    const res = await post(app, { ...baseBody, step3: '    ' });

    expect(res.status).toBe(200);
    const call = upsertSpy.mock.calls[0]![0] as SaveSurveyArgs;
    expect(call.step3).toBeNull();
  });

  it('step3 앞뒤 공백 → trim 된 값 저장', async () => {
    const { app, upsertSpy } = buildApp();
    const res = await post(app, { ...baseBody, step3: '  고민 텍스트  ' });

    expect(res.status).toBe(200);
    const call = upsertSpy.mock.calls[0]![0] as SaveSurveyArgs;
    expect(call.step3).toBe('고민 텍스트');
  });

  it('step3 null 명시 → null 저장', async () => {
    const { app, upsertSpy } = buildApp();
    const res = await post(app, { ...baseBody, step3: null });

    expect(res.status).toBe(200);
    const call = upsertSpy.mock.calls[0]![0] as SaveSurveyArgs;
    expect(call.step3).toBeNull();
  });

  it('step3 101자 → 400', async () => {
    const { app, upsertSpy } = buildApp();
    const res = await post(app, { ...baseBody, step3: 'x'.repeat(101) });

    expect(res.status).toBe(400);
    expect(upsertSpy).not.toHaveBeenCalled();
  });

  it('step1 원소가 49자 → 400', async () => {
    const { app } = buildApp();
    const res = await post(app, { ...baseBody, step1: ['x'.repeat(49)] });
    expect(res.status).toBe(400);
  });

  it('step1 원소 11개 → 400', async () => {
    const { app } = buildApp();
    const res = await post(app, {
      ...baseBody,
      step1: Array.from({ length: 11 }, (_, i) => `opt_${i}`),
    });
    expect(res.status).toBe(400);
  });

  it('step1 빈 배열 → 200 (선택 안 함 허용)', async () => {
    const { app } = buildApp();
    const res = await post(app, { ...baseBody, step1: [], step2: [] });
    expect(res.status).toBe(200);
  });

  it('surveyVersion 에 한글 → 400', async () => {
    const { app } = buildApp();
    const res = await post(app, { ...baseBody, surveyVersion: '버전1' });
    expect(res.status).toBe(400);
  });

  it('surveyVersion 17자 → 400', async () => {
    const { app } = buildApp();
    const res = await post(app, { ...baseBody, surveyVersion: 'a'.repeat(17) });
    expect(res.status).toBe(400);
  });

  it('sajuRequestId 포맷 어긋남 → 400', async () => {
    const { app, existsSpy } = buildApp();
    const res = await post(app, { ...baseBody, sajuRequestId: 'svr_short' });
    expect(res.status).toBe(400);
    expect(existsSpy).not.toHaveBeenCalled();
  });

  it('존재하지 않는 sajuRequestId → 404 NOT_FOUND', async () => {
    const { app, upsertSpy } = buildApp({
      sajuRequestExists: (async () => false) as unknown as SajuSurveyDeps['sajuRequestExists'],
    });
    const res = await post(app, baseBody);

    expect(res.status).toBe(404);
    const body = (await res.json()) as { error: string; detail: { entity: string } };
    expect(body.error).toBe('NOT_FOUND');
    expect(body.detail.entity).toBe('sajuRequest');
    expect(upsertSpy).not.toHaveBeenCalled();
  });

  it('upsert 내부 예외 → 500 INTERNAL_ERROR, 스택 미노출', async () => {
    const { app } = buildApp({
      upsertSurvey: (async () => {
        throw new Error('db exploded with secret info');
      }) as unknown as SajuSurveyDeps['upsertSurvey'],
    });
    const res = await post(app, baseBody);

    expect(res.status).toBe(500);
    const text = await res.text();
    expect(text).toContain('INTERNAL_ERROR');
    expect(text).not.toContain('secret info');
  });

  it('JSON 파싱 실패 → 400', async () => {
    const { app } = buildApp();
    const res = await app.fetch(
      new Request('http://localhost/api/saju/survey', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{not json',
      })
    );
    expect(res.status).toBe(400);
  });
});
