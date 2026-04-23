# AGENTS.md

> dohwa-backend — 도화선(Dohwaseon) 캐릭터 기반 연예운 사주 서비스 백엔드

## Quick Reference

- **언어**: 모든 응답 한국어 (기술 용어는 영문 병기 가능)
- **기술 스택**: TypeScript (ES2022, strict), Node.js 20+, Hono, Zod, Prisma + MySQL, date-fns
- **빌드**: `npm run build` | **린트**: `npm run lint` | **테스트**: `npm test`
- **REST 개발 서버**: `npm run dev` (기본 포트 8000)
- **DB 기동**: `docker compose up -d mysql && npm run prisma:migrate`
- **계약 원본**: `../dohwa_frontend/docs/backend-integration.md` (프론트·백 단일 소스)

## 제품 플로

1. **무료 사주** (`POST /api/saju/free`) — 프론트 입력 → `calculateSaju` → 영업 비밀 필드 제거한 `{pillars, highlight, sajuRequestId}` 반환. **LLM 호출 없음**.
2. **유료 리포트** (PR 별도) — 결제 검증 → `sajuRequestId` 로 명식 재사용 → 캐릭터별 Claude API 프롬프트 → 리포트 생성 → DB 저장.

## Core Rules (절대 불변)

1. `src/lib/saju.ts` 의 사주 파이프라인 10단계 순서 변경/건너뛰기 절대 금지
2. `eslint-disable`, `@ts-ignore` 사용 절대 금지
3. 코드 수정 후 반드시 `npm run lint` 실행, 에러 0건 확인
4. `solar_terms_*.ts`, `lunar_table_*.ts` 데이터 테이블 수동 편집 금지
5. 에러 메시지 한국어 + 올바른 형식 안내
6. **API 응답 영업 비밀 정책** — 명리 표준 계산 결과는 표시용으로 공개하되, 내부 판정 근거·수치·텍스트는 차단한다. 트랜스포머(`src/http/transformers/`)가 유일한 통로.
   - **공개 OK (표시용)**: 4기둥 한자/한글, `stemElement`·`branchElement` 파생 표시값, `yinYang`, 오행 counts/ratios/judgments, 십성 배열, 십이운성, 신살 배열(위치 포함), 용신·희신·기신 오행, 신강신약 7단계 라벨+position, 대운 배열.
   - **차단 (내부 근거/수치)**: `yongSin.reasoning`, `dayMasterStrength.score`/`analysis`, `gyeokGuk` 세부, `jiJangGan` 세부, `branchRelations` 세부, `wolRyeong`, `tenGodsDistribution`, `specialMarks`, `dominantElements`/`weakElements`, 그리고 **PR3 Claude 프롬프트·캐릭터 톤 설정·해석 텍스트**, `school_interpreter` 내부 가중치.
7. **무료 플로에서 LLM 호출 금지** — 결제 검증 이후에만 Claude API 진입 (유료 도메인 PR 이후).
8. **개인정보(생년월일·출생시각·성별·출생지) 로그 출력 금지.** 구조화 로거에서 필드 제외 또는 마스킹.
9. 결제 전 생성된 `SajuRequest` 레코드의 장기 보관 정책은 별도 PR에서 결정 (현재는 영구 저장).

## 디렉토리 구조 (PR1 기준)

```
src/
 ├ http/
 │   ├ routes/            REST 라우트 (hono)
 │   ├ transformers/      SajuData → 표시용 DTO (영업 비밀 차단막)
 │   ├ schemas/           Zod 요청 스키마
 │   ├ middleware/        CORS 등
 │   └ errors.ts          에러 코드 상수
 ├ db/
 │   └ client.ts          Prisma 싱글톤
 ├ lib/                   사주 계산 엔진 (수정 금지 — Core Rule #1)
 ├ data/                  정적 테이블 (수정 금지 — Core Rule #4)
 ├ types/                 공용 타입
 ├ utils/                 공용 유틸
 ├ benchmark/             계산 성능 측정
 └ server-rest.ts         REST 서버 진입점

prisma/schema.prisma      DB 스키마
docker-compose.yml        MySQL 서비스
```

## 아키텍처 원칙 (DDD + Hexagonal)

백엔드는 **Hexagonal Architecture (Ports & Adapters) + Domain-Driven Design** 을 지향한다. 현 `src/` 구조는 이 원칙의 80%를 만족하며, **신규 도메인(예: payment, reading)은 아래 템플릿 구조로 신규 작성**한다. 기존 `saju` 도메인의 전면 리네임은 별도 PR.

### 레이어와 의존성 방향

```
Adapter → Application → Domain
Infrastructure → Adapter / Application
```

의존성은 **항상 안쪽(Domain)으로만 흐른다.** Domain 이 Application 이나 Adapter 를 import 하면 안 된다.

| 레이어 | 책임 | 현재 위치 | 신규 도메인 위치 |
|---|---|---|---|
| Domain | 엔티티·값 객체·도메인 서비스·비즈니스 규칙 (순수 TS) | `src/lib/`, `src/data/`, `src/types/` | `src/domains/<name>/domain/` |
| Application | UseCase 오케스트레이션 · Request/Response DTO | `src/http/schemas/` (request), `src/http/transformers/` (response) — UseCase 는 현재 routes 에 섞여 있음 | `src/domains/<name>/application/{usecase,request,response}/` |
| Adapter (Inbound) | REST 라우터 — Request 수신 → UseCase 호출 → Response 반환 | `src/http/routes/` | `src/domains/<name>/adapter/inbound/api/` |
| Adapter (Outbound) | Repository 구현 · 외부 API 클라이언트 | `src/server-rest.ts` 클로저의 prisma 호출 (Repository 패턴 미정립) | `src/domains/<name>/adapter/outbound/{persistence,external}/` |
| Infrastructure (도메인별) | ORM 모델 + Mapper | `prisma/schema.prisma` (공용) | `src/domains/<name>/infrastructure/{orm,mapper}/` |
| Infrastructure (전역) | DB 세션·캐시·환경설정·로깅 | `src/db/client.ts`, `src/lib/performance_cache.ts` | `src/infrastructure/{database,cache,config,external}/` |

### MUST 규칙

**Domain Layer**
- Hono, Prisma, Zod, node:* I/O, 환경변수(`process.env`), Claude/external API 를 **import 금지**
- 순수 TypeScript 만 허용 (타입 · 상수 · 순수 함수 · 클래스)
- 외부 상태(DB, 캐시, 네트워크)에 의존 금지

**Application Layer**
- UseCase 는 외부 시스템을 **Port(인터페이스)** 로만 받는다. 구체 구현은 DI 로 주입.
- Hono `Context`, Prisma Client, HTTP 클라이언트 직접 사용 금지
- Request/Response DTO 는 **Domain Entity 와 반드시 분리** — 도메인 타입을 API 응답으로 직통 반환 금지

**Adapter (Inbound / Router)**
- 라우터에 **비즈니스 로직 작성 금지** — DTO 검증 → UseCase 호출 → DTO 반환만
- 현재 `createFreeSajuRoute(deps)` 의 DI 팩토리 패턴을 신규 라우트도 동일하게 따른다

**Adapter (Outbound / Repository)**
- Prisma Client 호출은 Outbound Adapter 안에서만 (`adapter/outbound/persistence`)
- UseCase 는 `SajuRepository` 같은 **추상 Port 인터페이스** 에만 의존

**Infrastructure**
- Prisma 모델(ORM) ↔ Domain Entity 는 **Mapper 로 변환** — ORM 타입을 도메인 로직·UseCase 에 그대로 노출 금지 (예외: 현 `SajuData` 는 lib 자체 타입이라 Mapper 불필요)
- 환경변수는 `src/infrastructure/config/` 의 단일 모듈에서만 읽는다 (도메인·UseCase 는 `process.env` 접근 금지)
- 캐시(`performance_cache.ts` 등)는 `src/infrastructure/cache/` 로 이동 대상 — 기존 코드는 유지하되 신규 캐시는 여기에 둔다

### 금지 사항 (하면 PR 반려)

- Domain 파일에서 `import { Hono } ...` / `import { PrismaClient } ...` / `import { anthropic } ...`
- Application(UseCase)에서 `new PrismaClient()` · `fetch('https://...')` 직접 호출
- Router에서 계산·분기 로직 (2줄 초과 시 UseCase 로 추출)
- ORM 모델을 Request/Response DTO 로 재사용
- 환경변수(`process.env.X`)를 `src/lib/` 또는 `src/domains/*/domain/` 에서 읽기

### 현 상태 vs 템플릿 갭 (기록용, 신규 PR 계기로 정리)

| 갭 | 현재 | 이상 | 정리 시점 |
|---|---|---|---|
| UseCase 분리 부족 | `routes/freeSaju.ts` 에 오케스트레이션 혼재 | `application/usecase/calculateFreeSaju.ts` | 전면 리네임 PR |
| Repository 패턴 부재 | `server-rest.ts` 에서 `prisma.sajuRequest.create` 직접 | `SajuRepository` 인터페이스 + Prisma 구현 | PR2(페이앱) 동반 |
| 캐시 위치 | `src/lib/performance_cache.ts` | `src/infrastructure/cache/` | 전면 리네임 PR |
| Mapper 부재 | `SajuData` 를 도메인·저장·응답에서 공유 | 저장용은 별도 모델 + Mapper | 결제 이후 장기 보관 정책 정할 때 |

## Document Map

### Architecture & Design
| 문서 | 내용 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 시스템 아키텍처 개요 (진입점) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 도메인 맵, 레이어 구조, 파이프라인 상세 |
| [docs/DESIGN.md](docs/DESIGN.md) | 설계 원칙, 기술 결정 근거 |
| [docs/design-docs/](docs/design-docs/) | 세부 설계 문서 |

### Quality & Reliability
| 문서 | 내용 |
|------|------|
| [docs/QUALITY.md](docs/QUALITY.md) | 도메인/레이어별 품질 평가 |
| [docs/RELIABILITY.md](docs/RELIABILITY.md) | 신뢰성 기준, 계산 불변량 |
| [docs/SECURITY.md](docs/SECURITY.md) | 보안 고려사항 |

### Reference
| 문서 | 내용 |
|------|------|
| [docs/references/rest-api.md](docs/references/rest-api.md) | REST API 엔드포인트 명세 |
| [docs/references/interpretation-guide.md](docs/references/interpretation-guide.md) | 명리 해석 가이드 |
| [docs/references/glossary.md](docs/references/glossary.md) | 사주 용어집 |

### Execution
| 문서 | 내용 |
|------|------|
| [docs/exec-plans/active/](docs/exec-plans/active/) | 진행 중인 작업 계획 |
| [docs/exec-plans/tech-debt-tracker.md](docs/exec-plans/tech-debt-tracker.md) | 기술 부채 추적 |

## REST 라우트 추가 체크리스트

**기존 `saju` 도메인 확장 시** (현 `src/http/` 구조 유지)
1. `src/http/schemas/` 에 Zod 요청 스키마 작성
2. `src/http/transformers/` 에 도메인 → DTO 변환 (영업 비밀 차단)
3. `src/http/routes/` 에 라우트 팩토리 (`createXxxRoute(deps)`) 작성 — DI 패턴
4. `src/server-rest.ts` 에 `app.route(...)` 등록 + 실제 deps 주입
5. `tests/http/` 에 트랜스포머 단위 테스트 + 라우트 통합 테스트(DI 스텁)
6. `docs/references/rest-api.md` 에 엔드포인트 스펙 추가
7. `npm run lint && npm test` 통과 확인

**신규 도메인 추가 시** (DDD 템플릿 구조 적용 — PR2 이후)
1. `src/domains/<name>/domain/` 에 Entity / Value Object / Domain Service 작성 (순수 TS, 외부 import 금지)
2. `src/domains/<name>/application/request,response/` 에 Zod 기반 DTO 정의
3. `src/domains/<name>/application/usecase/` 에 UseCase 구현 — Port 인터페이스만 의존
4. `src/domains/<name>/adapter/outbound/persistence/` 에 Repository Port 인터페이스 + Prisma 구현
5. `src/domains/<name>/adapter/outbound/external/` 에 외부 API 클라이언트 (필요 시)
6. `src/domains/<name>/adapter/inbound/api/` 에 Hono 라우터 — UseCase 호출만
7. `src/domains/<name>/infrastructure/{orm,mapper}/` 에 ORM ↔ Entity Mapper
8. `src/server-rest.ts` 에 라우터 등록 + DI 와이어링
9. 테스트 + `docs/references/rest-api.md` + 린트/테스트 통과

## Pre-Implementation Checklist

신규 기능 착수 전 확인:
- `../dohwa_frontend/docs/backend-integration.md` 최신 계약 확인
- 개인정보·영업 비밀·비용 게이트 중 어느 규칙이 적용되는지 식별
- `src/lib/saju.ts` 를 수정하지 않고 문제를 해결할 수 있는지 (수정이 필요하다 싶으면 재검토)
- **신규 도메인인지 기존 `saju` 확장인지 판별** → 체크리스트 경로 선택 (위 "REST 라우트 추가 체크리스트")
- 작성할 코드가 어느 레이어에 속하는지 먼저 결정 (Domain / Application / Adapter / Infrastructure) — 레이어 위반이면 즉시 재배치
