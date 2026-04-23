# PR1.5 — `/api/saju/survey` 엔드포인트 구현 계획

## Context

PR1(`/api/saju/free`)이 `sajuRequestId`를 발급·저장하는 구조는 갖췄지만, 프론트의 **3단 설문**(상황 선택지 · 관심사 선택지 · 자유 고민 텍스트)은 아직 백엔드로 흘러오지 않는다. 이 설문은 향후 PR3 유료 리포트에서 Claude 프롬프트 컨텍스트로 쓰일 데이터이며, **결제 전 익명 사용자 응답도 수집**해 프롬프트 튜닝·제품 개선에 활용하는 것이 경영 판단.

PR1.5는 이 수집 파이프를 작게 뚫는 것에만 집중한다. 유료 리포트 자체 구현은 PR3.

## 범위 (명시)

포함:
- `POST /api/saju/survey` 엔드포인트 (hono, DI 패턴)
- `SajuSurvey` Prisma 모델 + 마이그레이션
- Zod 요청 스키마 (구조만 검증 — 내용·슬러그 의미는 백엔드가 모름)
- `NOT_FOUND` 에러 헬퍼 (`errors.ts`)
- DI 스텁 기반 통합 테스트
- `docs/references/rest-api.md` 갱신

제외:
- 유료 리포트 생성 (PR3)
- 결제 연동 (PR2)
- 설문 응답 보관 기간 자동 파기 잡 (별도 — Core Rule #9 연장선)
- 프론트 키 카탈로그 문서화 (`backend-integration.md`는 프론트 레포 소관 — 필요 시 본 PR에서 PR 제안만 남김)

## 설계 원칙

1. **백엔드는 설문 내용에 무지** — step1/step2는 불투명 문자열 배열. 키(`"waiting_new"`)든 라벨("새로운 인연...")이든 백엔드는 검증 안 함. 프론트·분석 쪽이 해석 책임.
2. **버전 태그로 변경 수용** — `surveyVersion`(예: `"v1"`)이 함께 저장. 선택지 구조가 바뀌면 프론트가 `"v2"`로 올림. 백엔드 코드·스키마 불변.
3. **sajuRequestId 1:1 강제** — 같은 `sajuRequestId` 재제출은 upsert로 덮어씀. "최근 row 고르기" 패턴 원천 차단 (지난 대화의 동시성 리스크 #4 대응).
4. **인증 없음, 그러나 안전** — 읽기 API가 아니라 쓰기 API. opaque 키 + 길이·개수 상한 + FK 존재 확인. 남의 `sajuRequestId`를 알아도 **남의 설문을 덮어쓸 뿐** 정보 탈취 불가.
5. **step3 자유 텍스트 최소 취급** — 로그 금지(Core Rule #8 연장), 100자 하드 리밋, trim 후 빈 문자열은 null.

## 확정 계약

### 요청

```json
POST /api/saju/survey
{
  "sajuRequestId": "svr_01KPQ...",
  "surveyVersion": "v1",
  "step1": ["waiting_new", "dating"],
  "step2": ["destined", "timing"],
  "step3": "요즘 고민 텍스트..."   // optional / null / 생략 허용
}
```

### 응답

```
200 { "ok": true }
400 { "error": "BAD_REQUEST", "detail": [ZodIssue...] }
404 { "error": "NOT_FOUND", "detail": { "entity": "sajuRequest" } }
500 { "error": "INTERNAL_ERROR" }
```

### 검증 상한 (구조만)

| 필드 | 제약 |
|---|---|
| `sajuRequestId` | 정규식 `^svr_[0-9A-Z]{26}$` |
| `surveyVersion` | 1~16자, `[a-z0-9_.-]+` (대소문자 허용) |
| `step1`, `step2` | 최대 10개 원소, 각 원소 1~48자 문자열 |
| `step3` | 최대 100자, 생략 / null / trim 후 빈 문자열 허용 |

## Prisma 스키마 변경

`SajuSurvey` 신규 + `SajuRequest`에 reverse relation 추가.

```prisma
model SajuRequest {
  // ... 기존 필드 유지
  survey     SajuSurvey?
}

model SajuSurvey {
  id             String   @id @db.VarChar(40)   // "svy_" + ULID
  sajuRequestId  String   @unique @db.VarChar(40)
  surveyVersion  String   @db.VarChar(16)       // "v1", "v2"...
  step1          Json                            // string[]
  step2          Json                            // string[]
  step3          String?  @db.Text               // 자유 텍스트, null 허용
  paid           Boolean  @default(false)        // 결제 성사 시 true로 승격 (PR2에서 사용)
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  sajuRequest    SajuRequest @relation(fields: [sajuRequestId], references: [id], onDelete: Cascade)

  @@map("saju_survey")
  @@index([paid, createdAt])                     // 보관기간 정리 잡용 (별도 PR)
}
```

마이그레이션 이름: `add_saju_survey`

## 신규/변경 파일

```
prisma/schema.prisma                 # SajuSurvey 추가, SajuRequest에 reverse relation
prisma/migrations/*_add_saju_survey/ # 자동 생성

src/http/
 ├ schemas/
 │   └ sajuSurvey.ts                 # Zod 요청 스키마
 ├ routes/
 │   └ sajuSurvey.ts                 # POST /api/saju/survey 핸들러 (DI 팩토리)
 └ errors.ts                         # notFound() 헬퍼 추가

src/server-rest.ts                   # createSajuSurveyRoute 등록 + Prisma 의존성 주입

tests/http/
 └ sajuSurvey.route.test.ts          # DI 스텁 기반 통합 테스트

docs/references/rest-api.md          # 엔드포인트 스펙 섹션 추가
```

## 라우트 구현 플로

```
1) Zod 검증 → 실패 시 400 BAD_REQUEST
2) sajuRequestId 존재 확인 → 없으면 404 NOT_FOUND
   (FK 예외에 의존하지 않고 명시 검증 — 400/500 혼동 방지)
3) step3 trim 후 빈 문자열 → null 치환
4) upsert({
     where: { sajuRequestId },
     create: { id: "svy_"+ulid(), sajuRequestId, surveyVersion, step1, step2, step3 },
     update: { surveyVersion, step1, step2, step3 }
   })
5) 200 { ok: true }
6) 전역 catch → 500 INTERNAL_ERROR (서버 로그에 스택)
```

## 테스트 항목

| 케이스 | 기대 |
|---|---|
| 정상 요청 | 200 `{ok:true}`, upsertSpy 1회 호출 |
| 재제출 동일 sajuRequestId | 200, update 경로 타는지 확인 |
| step3 생략 | 200, step3 필드 null로 전달되는지 |
| step3 공백만("   ") | 200, trim 결과 null 저장 |
| step3 101자 | 400 |
| step1 배열에 49자 원소 | 400 |
| step1 11개 원소 | 400 |
| surveyVersion 한글 | 400 |
| sajuRequestId 포맷 불일치 | 400 |
| 존재하지 않는 sajuRequestId | 404 `{error:"NOT_FOUND"}` |
| upsert 내부 예외 | 500, 스택 미노출 |

## 완료 정의

1. `npm run lint` 0 errors
2. `npm test` 통과 (기존 + 신규)
3. `npx prisma migrate dev --name add_saju_survey` 성공, `saju_survey` 테이블 생성 확인
4. curl 라이브 스모크 테스트:
   ```bash
   # 사전: /api/saju/free 로 sajuRequestId 받아두기
   curl -X POST http://localhost:8000/api/saju/survey \
     -H "Content-Type: application/json" \
     -d '{"sajuRequestId":"svr_...","surveyVersion":"v1",
          "step1":["waiting_new"],"step2":["destined"],
          "step3":"테스트 고민"}'
   # → {"ok":true}
   # DB 확인: SELECT * FROM saju_survey;
   ```
5. Core Rule 준수: `@ts-ignore`/`eslint-disable` 없음, `src/lib/` 미수정, 개인정보 로그 출력 없음

## 의존/후속

- 후속 (PR2 이후): `paid` 승격 잡 (결제 webhook에서 해당 `sajuRequestId`의 survey row `paid=true`로)
- 후속 (별도): `paid=false && createdAt < now()-90d` row의 step3 자유 텍스트 null 익명화 배치
- 프론트 요청: `backend-integration.md` §6에 버전별 슬러그 키 카탈로그 섹션 추가 (프론트 PR)
