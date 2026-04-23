/**
 * POST /api/saju/survey
 * 사용자 설문 응답 저장 엔드포인트 (무료/유료 무관하게 수집).
 *
 * 플로:
 *   1) Zod 검증 (실패 → 400 BAD_REQUEST)
 *   2) sajuRequestId 존재 확인 (없으면 404 NOT_FOUND)
 *   3) step3 trim 후 공백만 남으면 null 로 치환 (저장 전 정규화)
 *   4) upsert — 같은 sajuRequestId 재제출은 덮어씀 ("최근 row 고르기" 금지)
 *   5) 200 { ok: true }
 *   6) 전역 catch → 500 INTERNAL_ERROR (스택은 서버 로그에만)
 *
 * 의존성 주입: 테스트에서 sajuRequest 조회기 / survey upsert 기 / ID 발급기 교체 가능.
 */

import { Hono } from 'hono';
import { sajuSurveyRequestSchema } from '../schemas/sajuSurvey.js';
import { badRequest, internalError, notFound } from '../errors.js';

export interface SaveSurveyArgs {
  id: string;
  sajuRequestId: string;
  surveyVersion: string;
  step1: string[];
  step2: string[];
  step3: string | null;
}

export interface SajuSurveyDeps {
  sajuRequestExists: (id: string) => Promise<boolean>;
  upsertSurvey: (args: SaveSurveyArgs) => Promise<void>;
  newSurveyId: () => string;
}

function normalizeStep3(input: string | null | undefined): string | null {
  if (input == null) return null;
  const trimmed = input.trim();
  return trimmed.length === 0 ? null : trimmed;
}

export function createSajuSurveyRoute(deps: SajuSurveyDeps): Hono {
  const route = new Hono();

  route.post('/', async (c) => {
    let body: unknown;
    try {
      body = await c.req.json();
    } catch {
      return c.json(badRequest([{ path: [], message: 'invalid JSON body' }]), 400);
    }

    const parsed = sajuSurveyRequestSchema.safeParse(body);
    if (!parsed.success) {
      return c.json(badRequest(parsed.error.issues), 400);
    }

    const { sajuRequestId, surveyVersion, step1, step2, step3 } = parsed.data;

    try {
      const exists = await deps.sajuRequestExists(sajuRequestId);
      if (!exists) {
        return c.json(notFound('sajuRequest'), 404);
      }

      await deps.upsertSurvey({
        id: deps.newSurveyId(),
        sajuRequestId,
        surveyVersion,
        step1,
        step2,
        step3: normalizeStep3(step3),
      });

      return c.json({ ok: true }, 200);
    } catch (err) {
      console.error('[sajuSurvey] persistence failed', err);
      return c.json(internalError(), 500);
    }
  });

  return route;
}
