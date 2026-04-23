/**
 * REST API 에러 응답 표준.
 * 클라이언트에는 코드만 노출하고, 스택/내부 메시지는 서버 로그에만 기록한다.
 */

export type ApiErrorCode =
  | 'BAD_REQUEST'
  | 'CALCULATION_FAILED'
  | 'NOT_FOUND'
  | 'INTERNAL_ERROR';

export interface ApiErrorBody {
  error: ApiErrorCode;
  detail?: unknown;
}

export const badRequest = (detail: unknown): ApiErrorBody => ({
  error: 'BAD_REQUEST',
  detail,
});

export const calculationFailed = (): ApiErrorBody => ({
  error: 'CALCULATION_FAILED',
});

export const notFound = (entity: string): ApiErrorBody => ({
  error: 'NOT_FOUND',
  detail: { entity },
});

export const internalError = (): ApiErrorBody => ({
  error: 'INTERNAL_ERROR',
});
