/**
 * dohwa-backend REST 서버 진입점.
 * 프론트(Next.js) 의 `NEXT_PUBLIC_API_URL` 대상이 되는 단일 프로세스.
 */

import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { ulid } from 'ulid';
import { buildCors } from './http/middleware/cors.js';
import { createFreeSajuRoute } from './http/routes/freeSaju.js';
import { createSajuSurveyRoute } from './http/routes/sajuSurvey.js';
import { calculateSaju } from './lib/saju.js';
import { calculateDaeUn } from './lib/dae_un.js';
import { prisma } from './db/client.js';

const app = new Hono();

app.use('*', buildCors());

app.get('/health', (c) => c.json({ status: 'ok' }));

const freeSajuRoute = createFreeSajuRoute({
  calculateSaju,
  calculateDaeUn: (saju) => calculateDaeUn(saju),
  newRequestId: () => `svr_${ulid()}`,
  saveSajuRequest: async (args) => {
    await prisma.sajuRequest.create({
      data: {
        id: args.id,
        birth: new Date(`${args.birth}T00:00:00.000Z`),
        birthTime: args.birthTime,
        calendar: args.calendar,
        gender: args.gender,
        birthCity: args.birthCity,
        sajuData: args.sajuData as unknown as object,
      },
    });
  },
});

app.route('/api/saju/free', freeSajuRoute);

const sajuSurveyRoute = createSajuSurveyRoute({
  newSurveyId: () => `svy_${ulid()}`,
  sajuRequestExists: async (id) => {
    const found = await prisma.sajuRequest.findUnique({
      where: { id },
      select: { id: true },
    });
    return found !== null;
  },
  upsertSurvey: async (args) => {
    await prisma.sajuSurvey.upsert({
      where: { sajuRequestId: args.sajuRequestId },
      create: {
        id: args.id,
        sajuRequestId: args.sajuRequestId,
        surveyVersion: args.surveyVersion,
        step1: args.step1,
        step2: args.step2,
        step3: args.step3,
      },
      update: {
        surveyVersion: args.surveyVersion,
        step1: args.step1,
        step2: args.step2,
        step3: args.step3,
      },
    });
  },
});

app.route('/api/saju/survey', sajuSurveyRoute);

const port = Number(process.env.REST_PORT ?? 8000);

serve({ fetch: app.fetch, port }, (info) => {
  console.log(`[dohwa-backend] listening on :${info.port}`);
});

export { app };
