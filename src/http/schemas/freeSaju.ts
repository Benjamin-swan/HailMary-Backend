/**
 * POST /api/saju/free 요청 스키마.
 * 프론트엔드 계약(`dohwa_frontend/docs/backend-integration.md`)과 1:1 대응.
 */

import { z } from 'zod';

const ISO_DATE = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;
const HHMM = /^([01]\d|2[0-3]):([0-5]\d)$/;

export const freeSajuRequestSchema = z
  .object({
    birth: z.string().regex(ISO_DATE, 'birth must be YYYY-MM-DD'),
    calendar: z.enum(['solar', 'lunar']),
    time: z.union([z.string().regex(HHMM, 'time must be HH:MM'), z.literal('unknown')]),
    gender: z.enum(['male', 'female']),
  })
  .refine(
    (data) => {
      const year = Number(data.birth.slice(0, 4));
      return year >= 1900 && year <= 2200;
    },
    { message: 'birth year must be between 1900 and 2200', path: ['birth'] }
  );

export type FreeSajuRequest = z.infer<typeof freeSajuRequestSchema>;
