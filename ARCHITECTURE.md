# Architecture Overview

> dohwa-backend — 도화선(Dohwaseon) 캐릭터 기반 연예운 사주 서비스의 단일 백엔드

## System Context

```
[dohwa_frontend (Next.js, Vercel)]
          │  HTTPS (JSON)
          ▼
[dohwa-backend (hono + Node.js 20, 포트 8000)]
          │
          ├─▶ [MySQL 8.4]        Prisma ORM, saju_request 테이블
          └─▶ [Claude API]       유료 리포트 전용 (PR2+ 예정, PR1에선 호출 없음)

[PayApp]  ──webhook──▶  [dohwa-backend]   (PR2 예정)
```

도화선 프론트(`../dohwa_frontend`)만 소비하는 전용 REST 백엔드. MCP 서버 역할은 철수 완료 — 과거 `src/core/`, `src/tools/`, `src/index.ts`, `src/server-http.ts`, `src/smithery.ts`는 제거됨.

## 제품 플로

```
[1] 무료 사주   POST /api/saju/free
      - Zod 검증 → calculateSaju() → transformers 로 영업 비밀 제거
      - sajuRequestId 발급 후 DB 저장
      - LLM 호출 없음 (무비용)

[2] 결제        POST /api/payment/{prepare|webhook}    ← PR2 예정
      - 페이앱 SDK (프론트) + webhook 검증 (백엔드)

[3] 유료 리포트 POST /api/reading/premium              ← PR3 예정
      - 결제 검증 → sajuRequestId로 명식 재사용 → Claude 프롬프트 → DB 저장
```

## Layer Architecture

```
[진입점] src/server-rest.ts            hono 앱 + CORS + 라우트 등록

[L1] src/http/                         REST 표면 (영업 비밀 차단막)
      routes/       ─ 엔드포인트 핸들러 (DI 팩토리 패턴)
      schemas/      ─ Zod 요청 스키마 (프론트 계약 1:1)
      transformers/ ─ SajuData → 표시용 DTO 변환
      middleware/   ─ CORS
      errors.ts     ─ 에러 코드 상수

[L2] src/db/                           Prisma 싱글톤
      client.ts                        

[L2] src/lib/                          사주 계산 엔진 (불변)
      saju.ts  ─ 10단계 파이프라인 조율자
      yongsin/       ─ 용신 알고리즘 4종
      interpreters/  ─ 해석 유파 5종

[L3] src/data/                         정적 테이블 (1900-2200, 불변)
      천간·지지·오행·절기·음력·경도·직업 DB

[공용] src/types/ · src/utils/         타입 정의 + 유틸 (진태양시 보정 등)
```

**의존성 규칙**: 상위 → 하위만 허용. `http`는 `lib`의 내부 타입을 직접 응답으로 내보내지 않음 — `transformers`가 유일한 통로(영업 비밀 차단).

> 상세: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/design-docs/layer-rules.md](docs/design-docs/layer-rules.md)

## Core Pipeline: 사주 계산 10단계

```
입력 ─▶ [1] 음력→양력 ─▶ [2] 진태양시 보정
      ─▶ [3] 4기둥       ─▶ [4] 지장간 세력  ─▶ [5] 오행 집계
      ─▶ [6] 십성         ─▶ [7] 신살         ─▶ [8] 일간 강약
      ─▶ [9] 격국         ─▶ [10] 용신        ─▶ SajuData 출력
```

**불변 규칙**: 각 단계는 이전 결과에 의존. 순서 변경/건너뛰기 절대 금지 (Core Rule #1).

## 영업 비밀 차단막

무료 사주 확장 PR 이후 정책은 "명리 표준 계산 결과는 공개, 내부 판정 근거·수치·유파 가중치는 차단".

- **공개 (파생 DTO 로 노출)**: 4기둥 한자/한글, 음양, 오행 counts/ratios/judgments, 십성, 십이운성, 신살 배열(위치 포함), 용신·희신·기신 오행, 신강신약 7단계 라벨+position, 대운 7구간.
- **차단 (응답에 등장 금지)**: `yongSin.reasoning`, `dayMasterStrength.score`/`analysis`, `gyeokGuk` 세부, `jiJangGan` 세부, `branchRelations` 세부, `wolRyeong`, `tenGodsDistribution`, `specialMarks`, `dominantElements`/`weakElements`, PR3 Claude 프롬프트·해석 텍스트, `school_interpreter` 내부 가중치.

유일한 통로는 `src/http/transformers/`. `tests/http/transformers.test.ts` 가 내부 필드명·근거 텍스트 원문을 응답에서 grep 해 회귀 감시. 상세 매트릭스는 [docs/SECURITY.md](docs/SECURITY.md).

## External Dependencies

| 패키지 | 용도 |
|--------|------|
| `hono` / `@hono/node-server` | REST 프레임워크 |
| `@prisma/client` / `prisma` | MySQL ORM |
| `zod` | 입력 스키마 검증 |
| `ulid` | `sajuRequestId` 발급 |
| `date-fns` / `date-fns-tz` | 날짜·타임존 |

외부 API 의존성: **없음** (PR1 범위). PR2에서 페이앱, PR3에서 Claude API 추가 예정.

## Deployment

- **로컬 개발**: `docker compose up -d mysql && npm run prisma:migrate && npm run dev` (포트 8000)
- **빌드**: TypeScript → ES2022 (`dist/`), 실행은 `npm start`
- **프로덕션 호스팅**: 🟣 미정 (도화선 도메인 확정 후 결정)

## Status & Roadmap

| 단계 | 상태 |
|------|------|
| PR1 — `/api/saju/free` + MySQL + Docker | ✅ 구현·테스트 완료 (프론트 연동 검증 중) |
| PR2 — `/api/payment/prepare` + webhook (페이앱) | ⏳ 대기 |
| PR3 — `/api/reading/premium` (Claude API) | ⏳ PR2 의존 |
| 도메인 재구조화 `src/lib → src/domains/fortuneteller/lib` | ⏳ PR2/3 이후 |

진행 중 계획: [`docs/exec-plans/active/`](docs/exec-plans/active/)
