# Architecture

> dohwa-backend — 도화선(Dohwaseon) 연예운 사주 서비스의 REST 백엔드

## 도메인 맵

```
dohwa-backend/
├── prisma/
│   ├── schema.prisma                # SajuRequest 모델 (PR1)
│   └── migrations/
│
├── docker-compose.yml               # MySQL 8.4 로컬 스택
│
├── src/
│   ├── server-rest.ts               # [진입점] hono 앱 + CORS + 라우트 등록
│   │
│   ├── http/                        # [L1] REST 표면 (영업 비밀 차단막)
│   │   ├── errors.ts                #   에러 코드 상수 + 응답 유틸
│   │   ├── middleware/
│   │   │   └── cors.ts              #   환경변수 기반 origin 매칭
│   │   ├── schemas/
│   │   │   └── freeSaju.ts          #   POST /api/saju/free 요청 스키마
│   │   ├── transformers/            #   SajuData → 표시용 DTO
│   │   │   ├── hueMap.ts            #     오행 → hex 색상 매핑
│   │   │   ├── pillarView.ts        #     Pillar → {label, heaven, earth, element, hue, unknown}
│   │   │   ├── sinSalPosition.ts    #     도화·홍염·편관·정관 우선순위로 highlight 생성
│   │   │   └── sajuDisplay.ts       #     최종 응답 DTO 조립
│   │   └── routes/
│   │       └── freeSaju.ts          #   POST /api/saju/free (DI 팩토리)
│   │
│   ├── db/
│   │   └── client.ts                # [L2] Prisma 싱글톤
│   │
│   ├── lib/                         # [L2] 비즈니스 로직 (수정 금지 — Core Rule #1)
│   │   ├── saju.ts                  #   ** 메인 조율자 ** (10단계 파이프라인)
│   │   ├── calendar.ts              #   음양력 변환
│   │   ├── ten_gods.ts              #   십성 계산
│   │   ├── sin_sal.ts               #   신살 탐지 (15종)
│   │   ├── day_master_strength.ts   #   일간 강약
│   │   ├── gyeok_guk.ts             #   격국 결정
│   │   ├── yong_sin.ts              #   용신 선정
│   │   ├── dae_un.ts                #   대운 계산
│   │   ├── fortune.ts               #   운세 해석
│   │   ├── compatibility.ts         #   궁합 분석
│   │   ├── career_matcher.ts / career_recommendation.ts
│   │   ├── school_comparator.ts / school_interpreter.ts
│   │   ├── se_un.ts / wol_un.ts / si_un.ts     시간 단위별 운세
│   │   ├── daeun_analysis.ts / seyun_analysis.ts / wolun_analysis.ts / iljin_analysis.ts
│   │   ├── taekil_recommendation.ts / jakmeong_analysis.ts / pungsu_advice.ts / timing_advice.ts
│   │   ├── leap_month_analysis.ts / unified_data_query.ts / jijanggan_precise.ts
│   │   ├── interpretation_settings.ts          싱글톤 설정
│   │   ├── validation.ts / comprehensive_validation.ts
│   │   ├── constants.ts / helpers.ts / error_handler.ts
│   │   ├── api_cache.ts / performance_cache.ts
│   │   ├── yongsin/                 # [L2.1] 용신 알고리즘 서브시스템
│   │   │   ├── strength_algorithm.ts        강약용신
│   │   │   ├── seasonal_algorithm.ts        조후용신
│   │   │   ├── mediation_algorithm.ts       통관용신
│   │   │   ├── disease_algorithm.ts         병약용신
│   │   │   └── selector.ts                  통합 선택기
│   │   └── interpreters/            # [L2.2] 해석 유파 서브시스템
│   │       ├── ziping_interpreter.ts        자평명리
│   │       ├── modern_interpreter.ts        현대명리
│   │       └── index.ts                     적천수·궁통보감·신살중심 포함
│   │
│   ├── data/                        # [L3] 정적 테이블 (수정 금지 — Core Rule #4)
│   │   ├── heavenly_stems.ts        #   천간 10
│   │   ├── earthly_branches.ts      #   지지 12 + 지장간
│   │   ├── wuxing.ts                #   오행 관계
│   │   ├── solar_terms*.ts          #   절기 (1900-2200, 연도 분할)
│   │   ├── lunar_table*.ts          #   음력 (1900-2200, 연도 분할)
│   │   ├── longitude_table.ts       #   162개 시군구 경도
│   │   ├── modern_careers.ts        #   직업 DB 500+
│   │   ├── school_presets.ts / daeun_reference_table.ts
│   │   ├── jijanggan_strength_table.ts / manselyeok_table.ts
│   │
│   ├── types/                       # [공용] 타입 정의
│   │   ├── index.ts                 #   SajuData, Pillar, 리터럴 타입
│   │   └── interpretation.ts
│   │
│   ├── utils/                       # [공용] 유틸
│   │   └── date.ts                  #   진태양시 보정
│   │
│   ├── benchmark/                   # 계산 성능 측정
│   └── scripts/                     # 검증/생성 스크립트
│
├── tests/
│   ├── http/                        #   트랜스포머 단위 + 라우트 통합 (DI 스텁)
│   ├── jdn-verification.test.ts
│   ├── kasi-anchor-verification.test.ts
│   └── solar-terms-verification.test.ts
│
├── docs/                            #   설계·품질·레퍼런스·실행 계획
└── dist/                            # 빌드 출력 (ES2022)
```

## 레이어 구조 및 의존성 방향

```
[진입점] server-rest.ts
    ↓
[L1] http/        REST 표면
    │  routes → schemas/transformers/errors
    ↓
[L2] db/ (Prisma)  +  lib/          비즈니스 로직
                       ├── yongsin/       용신 알고리즘 4종
                       └── interpreters/  해석 유파 5종
    ↓
[L3] data/        정적 데이터 (천간, 지지, 절기, 음력, 경도, 직업)
    ↑
[공용] types/ + utils/   모든 레이어에서 참조 가능
```

**의존성 규칙**: 상위 → 하위만 허용. 역방향/순환 참조 금지.

| From \ To | http | db | lib | data | types/utils |
|-----------|------|----|----|------|-------------|
| http      | -    | O  | O  | x    | O           |
| db        | x    | -  | x  | x    | O           |
| lib       | x    | x  | O  | O    | O           |
| data      | x    | x  | x  | O    | O           |
| types     | x    | x  | x  | x    | O           |

> `http → lib` 참조 시 `SajuData` 원형은 응답에 그대로 나갈 수 없음. **반드시 `http/transformers/`를 경유** — 이것이 영업 비밀 차단막 (Core Rule #6).

## 핵심 파이프라인: 사주 계산 10단계

```
입력: birthDate, birthTime, calendar, isLeapMonth, gender, birthCity
                                    ↓
[1] calendar.ts           음력 → 양력 변환 (필요시)
                                    ↓
[2] utils/date.ts         진태양시 보정 (썸머타임 + 경도)
                                    ↓
[3] saju.ts               4기둥 계산 (년 → 월 → 일 → 시)
                                    ↓
[4] earthly_branches.ts   지장간 세력 계산 (당령/퇴기/진기)
                                    ↓
[5] saju.ts               오행 개수 집계 (wuxingCount)
                                    ↓
[6] ten_gods.ts           십성 분석
                                    ↓
[7] sin_sal.ts            신살 탐지 (15종)
                                    ↓
[8] day_master_strength.ts 일간 강약 평가
                                    ↓
[9] gyeok_guk.ts          격국 결정
                                    ↓
[10] yong_sin.ts          용신 선정 (4개 알고리즘 → selector)
                                    ↓
출력: SajuData (완전한 사주 분석 결과 — 내부 전용)
                                    ↓
                     [http/transformers/sajuDisplay.ts]
                                    ↓
        응답 DTO: { pillars[4], highlight, sajuRequestId }
```

**불변 규칙**: 각 단계는 이전 결과에 의존. 순서 변경/건너뛰기 금지 (Core Rule #1).

## REST 엔드포인트 현황

| 메서드·경로 | 상태 | 비고 |
|---|---|---|
| `GET /health` | ✅ | liveness probe |
| `POST /api/saju/free` | ✅ PR1 | 무료 사주, LLM 호출 없음, `sajuRequestId` 발급 |
| `POST /api/payment/prepare` | ⏳ PR2 | 페이앱 주문 생성, `orderId`/`amount` 반환 |
| `POST /api/payment/webhook` | ⏳ PR2 | 페이앱 feedbackurl 수신, 서명·금액 검증 |
| `POST /api/reading/premium` | ⏳ PR3 | 결제 검증 → 명식 재사용 → Claude API → 리포트 저장 |

상세 스펙: [`docs/references/rest-api.md`](references/rest-api.md)

## 주요 서브시스템

### 용신 알고리즘 (`lib/yongsin/`)
4개 독립 알고리즘이 `selector.ts`에서 통합:
- **강약용신** (strength) — 일간 강약 기반
- **조후용신** (seasonal) — 계절 한난조습 보정
- **통관용신** (mediation) — 충돌 오행 중재
- **병약용신** (disease) — 사주 불균형 치료

### 해석 유파 (`lib/interpreters/`)
5개 유파별 해석기: 자평명리(정통), 현대명리(실용), 적천수, 궁통보감, 신살중심

### 운세 시스템 (`lib/`)
시간 단위별 독립 모듈: 대운(10년) → 세운(연) → 월운 → 일진 → 시운

### 영업 비밀 차단막 (`src/http/transformers/`)
`SajuData` 원형은 응답에 그대로 나가지 않는다. 트랜스포머가 유일한 통로.

- **공개 (파생 DTO 로 노출)**: 4기둥 한자/한글·음양, 오행 counts/ratios/judgments, 십성, 십이운성, 신살(위치 포함), 용신·희신·기신 오행, 신강신약 7단계, 대운 7구간.
- **차단 (응답에 등장 금지)**: `yongSin.reasoning`, `dayMasterStrength.score`/`analysis`, `gyeokGuk` 세부, `jiJangGan` 세부, `branchRelations` 세부, `wolRyeong`, `tenGodsDistribution`, `specialMarks`, `dominantElements`/`weakElements`, PR3 Claude 프롬프트·해석 텍스트, `school_interpreter` 유파 가중치.

회귀 감시: `tests/http/transformers.test.ts` 의 내부 필드명 + 근거 텍스트 원문 grep 단언. 상세 정책: [SECURITY.md](SECURITY.md).

## 외부 의존성

| 패키지 | 용도 |
|--------|------|
| `hono` / `@hono/node-server` | REST 프레임워크 |
| `@prisma/client` / `prisma` | MySQL ORM |
| `zod` | 입력 스키마 검증 |
| `ulid` | `sajuRequestId` 발급 |
| `date-fns` / `date-fns-tz` | 날짜 처리 + 타임존 |

외부 API 의존성: **PR1에서 없음**.
- PR2: 페이앱 webhook 수신 (아웃바운드 없음, 인바운드만)
- PR3: Claude API (Anthropic SDK)

## 배포

- **로컬 개발**: `docker compose up -d mysql && npm run prisma:migrate && npm run dev` (포트 8000)
- **빌드**: `npm run build` → `dist/` (ES2022)
- **실행**: `npm start` (= `node dist/server-rest.js`)
- **프로덕션 호스팅**: 🟣 미정. 프로덕션 도메인 확정 시 CORS allow-origin 및 `NEXT_PUBLIC_API_URL` 동시 갱신 필요 (`backend-integration.md` §8 참조).

## 이력 (주요 마일스톤)

- **PR1 (2026-04)** — REST 백엔드로 전환. MCP 서버 철수 (`src/index.ts`, `src/server-http.ts`, `src/smithery.ts`, `src/core/`, `src/tools/`, `src/schemas/` 제거). hono + Prisma + MySQL + Docker 도입. `/api/saju/free` 구현.
