/**
 * POST /api/saju/survey 요청 스키마.
 * 백엔드는 선택지의 의미를 모름 — 구조(길이·개수·포맷)만 검증한다.
 * 문항/선택지가 바뀌어도 surveyVersion 만 올리면 스키마 불변.
 */

import { z } from 'zod';

const SAJU_REQUEST_ID = /^svr_[0-9A-Z]{26}$/;
const SURVEY_VERSION = /^[a-z0-9_.-]+$/i;

const stepOption = z.string().min(1).max(48);
const stepArray = z.array(stepOption).max(10);

export const sajuSurveyRequestSchema = z.object({
  sajuRequestId: z.string().regex(SAJU_REQUEST_ID, 'invalid sajuRequestId format'),
  surveyVersion: z.string().min(1).max(16).regex(SURVEY_VERSION, 'invalid surveyVersion format'),
  step1: stepArray,
  step2: stepArray,
  step3: z.string().max(100).nullable().optional(),
});

export type SajuSurveyRequest = z.infer<typeof sajuSurveyRequestSchema>;
