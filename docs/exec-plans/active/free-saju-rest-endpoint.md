# PR1 — `/api/saju/free` 엔드포인트 구현 계획

## Context

이 레포(현 `fortuneteller-main/`, PR1 이후 `dohwa_project/dohwa-backend/`로 승격)는 도화선 서비스의 **단일 백엔드**가 된다. 이전에 고려했던 Python/FastAPI 중간층은 폐기되었고, fortuneteller 계산 엔진을 이 레포의 `domains/fortuneteller/`로 흡수하여 Node.js/TypeScript 단일 프로세스에서 무료 사주 · 결제 · 유료 리포트를 모두 서빙한다.

**계약 원본**: `dohwa_frontend/docs/backend-integration.md` (프론트·백 양측 단일 소스)

**PR1 범위** — 무료 사주 엔드포인트 하나. 결제 / Claude 리포트 / 도메인 재구조화 전면 이관은 **별도 PR**로 분리.

## PR1 범위 (명시)

포함:
- `POST /api/saju/free` 엔드포인트 (hono 기반)
- Prisma + MySQL + Docker 스택 도입 (`saju_request` 테이블만)
- `sajuRequestId` 발급·저장 로직
- 입력 검증 · 트랜스포머 · 에러 처리 · CORS · 테스트

제외 (별도 PR):
- `POST /api/payment/prepare` · `POST /api/payment/webhook` (페이앱)
- `POST /api/reading/premium` (Claude API)
- `src/lib` → `src/domains/fortuneteller/lib` 디렉토리 재구조화
- 기존 MCP 서버(`src/index.ts`, `src/server-http.ts`) 철수 여부 결정
- 폴더 리네임(`fortuneteller-main` → `dohwa-backend`) — 이건 PR1과 별개로 한 번에 실행

## 확정 계약 (frontend single source 기준)

### 요청
```json
POST /api/saju/free
{
  "birth": "1998-03-15",        // ISO YYYY-MM-DD only (프론트가 변환 후 전송)
  "calendar": "solar" | "lunar",
  "time": "14:30" | "unknown",
  "gender": "male" | "female"
}
```
- `name`, `birthCity` 받지 않음
- 서버는 `birthCity = "서울"` 고정

### 응답 (성공 200)
```json
{
  "pillars": [
    { "label": "년주", "heaven": "甲", "earth": "子", "element": "목 / 수", "hue": "#9CC8B0", "unknown": false },
    { "label": "월주", "heaven": "丙", "earth": "寅", "element": "화 / 목", "hue": "#E6A88E", "unknown": false },
    { "label": "일주", "heaven": "戊", "earth": "申", "element": "토 / 금", "hue": "#E6C58E", "unknown": false },
    { "label": "시주", "heaven": "辛", "earth": "亥", "element": "금 / 수", "hue": "#6B8BB5", "unknown": false }
  ],
  "highlight": "도화살(桃花殺) — 일지(日支)에 위치",
  "sajuRequestId": "svr_01HXY..."
}
```
- `pillars` 항상 **길이 4 고정**
- `time === "unknown"` 이면 `pillars[3]`만 `{heaven:"?", earth:"?", element:"—", hue:"—", unknown:true}` (나머지 3개는 정상 계산)
- `insight` 필드 없음
- `highlight` 포맷 고정: `"{신살명}({한자}) — {위치(한자)}에 위치"`. 매칭 없으면 담백한 기본 문구(아래 참고)

### 에러
```json
400 { "error": "BAD_REQUEST", "detail": [{"path":["birth"], "message":"..."}] }
500 { "error": "CALCULATION_FAILED" }
```
- 500 응답에 스택·내부 변수 **절대 노출 금지**. 서버 로그에는 full stack 기록

### 오행 hue 팔레트 (확정)
| 오행 | hex |
|---|---|
| 목(木) | `#9CC8B0` |
| 화(火) | `#E6A88E` |
| 토(土) | `#E6C58E` |
| 금(金) | `#C5CAD4` |
| 수(水) | `#6B8BB5` |

혼합 오행일 때 `hue`는 **천간 오행 색** 기준.

### 응답 시간
- 평시 목표 500ms 이하
- 프론트 하드 타임아웃 5초
- 네트워크 왕복 + DB insert 포함이므로 여유 있게

## 작업 단계 (PR1 한정)

### 1. 의존성
- `dependencies`: `hono`, `@hono/node-server`, `zod`, `@prisma/client`, `ulid` (sajuRequestId 발급)
- `devDependencies`: `prisma`
- `scripts` 추가:
  - `dev:rest`: `tsx watch src/server-rest.ts`
  - `start:rest`: `node dist/server-rest.js`
  - `prisma:generate`: `prisma generate`
  - `prisma:migrate`: `prisma migrate dev`

### 2. Docker 스택
`docker-compose.yml`에 MySQL 서비스 추가 (기존 파일 확인 후 병합):
- `mysql:8.4` 이미지
- 환경변수: `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE=dohwa`
- 볼륨 영속화
- 3306 포트 로컬 노출 (개발용)
- API 서비스도 같은 compose에 둘지 선택 — 일단 MySQL만 compose, API는 로컬 개발 시 호스트 실행

### 3. Prisma 스키마
`prisma/schema.prisma`:
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}

model SajuRequest {
  id         String   @id                      // ulid, "svr_" prefix
  birth      DateTime                           // 생년월일 (시각 미포함)
  birthTime  String?                            // "HH:MM" or null (unknown)
  calendar   String                             // "solar" | "lunar"
  gender     String                             // "male" | "female"
  birthCity  String                             // "서울" 고정 (향후 확장 대비 컬럼 유지)
  // 계산 결과 캐시 (유료에서 재사용) — 전체 SajuData JSON
  sajuData   Json
  createdAt  DateTime @default(now())

  @@map("saju_request")
}
```
- `sajuData` 컬럼은 내부 저장용, API 응답에 나가지 않음. 유료 리포트 단계에서 재사용
- 개인정보(생년월일·시각·성별)는 최소 저장 — 결제 전엔 삭제 정책 고려 (PR2~)

### 4. 신규 파일 (PR1에서 추가만)

```
src/http/
 ├ schemas/
 │   └ freeSaju.ts              # Zod 요청 스키마
 ├ transformers/
 │   ├ hueMap.ts                # WuXing → hex 고정 맵
 │   ├ pillarView.ts            # Pillar → {label, heaven, earth, element, hue, unknown}
 │   ├ sinSalPosition.ts        # SajuData → {sinSal, pillarLabel} 유추 (도화>홍염>편관>정관)
 │   └ sajuDisplay.ts           # SajuData → FreeSajuResponse (상위 조합)
 ├ routes/
 │   └ freeSaju.ts              # POST /api/saju/free 핸들러
 ├ middleware/
 │   └ cors.ts                  # 환경별 origin 매칭
 └ errors.ts                    # 에러 코드 상수 + 응답 유틸

src/db/
 └ client.ts                    # PrismaClient 싱글톤

src/server-rest.ts              # hono app 엔트리

prisma/schema.prisma
.env.example                    # DATABASE_URL, CORS_ORIGINS 등
```

### 5. 구현 디테일

**`schemas/freeSaju.ts`**
```typescript
export const freeSajuSchema = z.object({
  birth: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),  // ISO only
  calendar: z.enum(["solar", "lunar"]),
  time: z.union([z.string().regex(/^\d{2}:\d{2}$/), z.literal("unknown")]),
  gender: z.enum(["male", "female"]),
}).refine(d => {
  const year = Number(d.birth.slice(0, 4));
  return year >= 1900 && year <= 2200;
}, { message: "birth year out of range", path: ["birth"] });
```

**`routes/freeSaju.ts`** 플로
1. Zod 검증 → 실패 시 400 `{error:"BAD_REQUEST", detail: parse.error.issues}`
2. `time === "unknown"` 플래그 보관, `calculateSaju()`에는 `"12:00"` 전달
3. `calculateSaju({birthDate: body.birth, birthTime: timeForCalc, calendar: body.calendar, isLeapMonth: false, gender: body.gender, birthCity: "서울"})`
4. sajuRequestId 발급 (`"svr_" + ulid()`)
5. DB insert (`prisma.sajuRequest.create`)
6. `sajuDisplay` transformer 호출 → `unknown` 플래그 true면 `pillars[3]`만 플레이스홀더로 대체
7. 응답 200 반환
8. 전역 catch → 500 `{error:"CALCULATION_FAILED"}` + 서버 로그에 stack

**`transformers/hueMap.ts`**
```typescript
export const HUE_MAP: Record<WuxingKorean, string> = {
  "목": "#9CC8B0",
  "화": "#E6A88E",
  "토": "#E6C58E",
  "금": "#C5CAD4",
  "수": "#6B8BB5",
};
```

**`transformers/sinSalPosition.ts`**
- 우선순위: `["do_hwa_sal", "hong_yeom_sal", "pyeon_gwan", "jeong_gwan"]`
- 첫 매칭 신살에 대해 `src/lib/sin_sal.ts` 판정 조건을 읽어 `["년지","월지","일지","시지"]` 중 해당 pillar 반환
- 매칭 없으면 담백한 기본 문구로 fallback (예: `"명식의 흐름 — 전반적으로 담백"`)
- 신살명 한자 표기 매핑 테이블: `do_hwa_sal → "도화살(桃花殺)"`, `hong_yeom_sal → "홍염살(紅艷殺)"` 등
- `time === "unknown"`이면 시주 기준 신살은 후보에서 제외

**`server-rest.ts`**
- hono 앱 + `hono/cors` 미들웨어 (env `CORS_ORIGINS` 콤마 분리)
- 라우트: `/health` (GET 200), `/api/saju/free` (POST)
- `/api/saju/premium`, `/api/payment/*`, `/api/reading/*` 는 **등록 안 함** (PR1 범위 아님)
- `serve({fetch: app.fetch, port: Number(process.env.REST_PORT ?? 8000)})`
- 기본 포트 8000 (프론트 integration 문서의 local 값과 일치)

### 6. 테스트
- `tests/http/transformer.test.ts` — 순수 함수 단위
  - hueMap 정확성
  - pillarView: 甲木 + 子水 → `{element: "목 / 수", hue: "#9CC8B0"}`
  - sinSalPosition: `do_hwa_sal` 케이스별 pillarLabel 정확성 + 없는 경우 fallback
  - sajuDisplay: **민감 필드(wuxingCount, jiJangGan, tenGods, dayMasterStrength, gyeokGuk, yongSin, branchRelations, sinSals 배열 전체, daeUn, strength 수치) 응답 객체에 부재** — key set 단언
- `tests/http/freeSaju.route.test.ts` — hono `app.fetch` 통합
  - `{birth:"1998-03-15", time:"14:30", solar, female}` → 200 + pillars[0].heaven 예상값
  - `time:"unknown"` → pillars[3].unknown === true, heaven === "?"
  - 1899년/2201년 → 400
  - birth 포맷 오류 (`"1998.03.15"`) → 400
  - DB insert는 테스트에서 mock (Prisma `$executeRaw` mock 또는 Vitest spyOn)
- `jest.config.js`에 db 통합 테스트는 별도 describe로 격리, 기본 테스트는 DB 없이 실행

### 7. 문서
- `docs/references/rest-api.md` 신규 — 엔드포인트 스펙 + curl 샘플
- `README.md` 에 "REST API (for dohwaseon frontend)" 섹션 추가
- `docs/FRONTEND.md` 업데이트

### 8. CLAUDE.md / AGENTS.md 규칙 준수
- [ ] `npm run lint` 에러 0건 (Core Rule #3)
- [ ] `@ts-ignore` / `eslint-disable` 사용 없음 (Core Rule #2)
- [ ] `src/lib/saju.ts` 수정 없음 (Core Rule #1)
- [ ] `solar_terms_*.ts`, `lunar_table_*.ts` 수정 없음 (Core Rule #4)
- [ ] 외부 네트워크 API 호출 추가 없음 — hono/Prisma는 프레임워크·DB 드라이버 (Core Rule #5 해당 아님)
- [ ] 에러 응답 한국어 매핑은 프론트 책임, 백엔드는 에러 코드만 (Core Rule #6)

## 의존 / 선행 작업

PR1 착수 **전에** 완료해야 할 것:
1. `C:\Users\skwog\Documents\dohwa_project\dohwa_backend\` (FastAPI CLAUDE.md 포함) 삭제
2. `C:\Users\skwog\Documents\dohwa_project\dohwa_backend\fortuneteller-main\` 내용을 `C:\Users\skwog\Documents\dohwa_project\dohwa-backend\`로 이동
3. `package.json` name을 `@dohwa/backend` 또는 유사하게 변경 (기존 `@hoshin/saju-mcp-server` 유지 여부 결정 필요)

## 핵심 파일 참조

- 계약 원본: `dohwa_frontend/docs/backend-integration.md`
- 입력 스키마 패턴: `src/core/tool-definitions.ts:13-53`
- 계산 엔트리: `src/lib/saju.ts:27` `calculateSaju()`
- SajuData 타입: `src/types/index.ts:66-155`
- SinSal enum: `src/types/index.ts:168-183`
- SinSal 판정 조건: `src/lib/sin_sal.ts`
- WuXing 한국어: `src/data/wuxing.ts:17-58`
- 프론트 응답 기대 shape: `dohwa_frontend/src/products/dohwaseon/scenes/saju/{doyoon,yeonwoo}/data/mockSaju.ts`

## 완료 정의

1. `npm run lint` 에러 0
2. `npm test` 통과 (기존 + 신규)
3. `docker compose up -d mysql && npm run prisma:migrate && npm run dev:rest` 로 서버 기동
4. curl 커맨드로 정상 응답 확인:
   ```bash
   curl -X POST http://localhost:8000/api/saju/free \
     -H "Content-Type: application/json" \
     -d '{"birth":"1998-03-15","calendar":"solar","time":"14:30","gender":"female"}'
   ```
5. 응답 JSON에 `wuxingCount`/`jiJangGan`/`tenGods`/`dayMasterStrength`/`gyeokGuk`/`yongSin`/`branchRelations`/`sinSals`(배열)/`daeUn` 문자열 **grep 0건**
6. `time:"unknown"`일 때 `pillars.length === 4 && pillars[3].unknown === true`
7. DB `saju_request` 테이블에 row 1개 기록되고 응답의 `sajuRequestId`와 매칭
8. 기존 MCP 서버(`npm start`, `npm run start:http`) 회귀 없음
