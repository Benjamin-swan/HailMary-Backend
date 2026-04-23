/**
 * CORS 미들웨어.
 * 환경변수 `CORS_ORIGINS` 콤마 분리 리스트로 허용 오리진을 관리.
 * 프로덕션에서는 와일드카드 금지, 도메인 정확 매칭만.
 */

import { cors } from 'hono/cors';

export function buildCors() {
  const raw = process.env.CORS_ORIGINS ?? 'http://localhost:3000';
  const allowed = raw
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  return cors({
    origin: (origin) => (allowed.includes(origin) ? origin : null),
    allowMethods: ['GET', 'POST', 'OPTIONS'],
    allowHeaders: ['Content-Type'],
    maxAge: 600,
  });
}
