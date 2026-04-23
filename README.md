# dohwa-backend

도화선(Dohwaseon) 캐릭터 기반 연예운 사주 서비스의 백엔드.

- **프론트엔드**: `../dohwa_frontend` (Next.js 16, Vercel 배포)
- **계약 원본**: [`../dohwa_frontend/docs/backend-integration.md`](../dohwa_frontend/docs/backend-integration.md)
- **엔드포인트 명세**: [`docs/references/rest-api.md`](docs/references/rest-api.md)

## 제품 플로

1. **무료 사주** — 프론트가 생년월일/시각/성별/양음력을 보내면 사주팔자를 계산해 표시용 데이터만 반환 (LLM 호출 없음)
2. **유료 리포트 (별도 PR)** — 결제 검증 후 캐릭터별 Claude API 프롬프트로 연예운 리포트 생성

## 기술 스택

- TypeScript (ES2022, strict) / Node.js 20+
- [Hono](https://hono.dev/) + `@hono/node-server` (REST)
- [Prisma](https://www.prisma.io/) + MySQL 8.4 (docker-compose)
- Zod (입력 검증), date-fns / date-fns-tz
- Jest + ts-jest (테스트), ESLint (린트)

내부 사주 계산 엔진은 `src/lib/` 에 위치 — 로컬 테이블 기반이며 외부 데이터 API 의존성 없음 (1900–2200 년 만세력, 162개 시군구 경도, 24절기 등).

## 시작하기

### 사전 준비

- Node.js 20 이상
- Docker Desktop (MySQL 용)

### 설치

```bash
npm install
cp .env.example .env
```

### MySQL + 마이그레이션

```bash
docker compose up -d mysql
npx prisma generate
npm run prisma:migrate
```

### 개발 서버

```bash
npm run dev
```

`http://localhost:8000` 에서 기동. `/health` 로 상태 확인.

### 테스트 · 린트

```bash
npm run lint
npm test
```

### 빠른 호출 확인

```bash
curl -X POST http://localhost:8000/api/saju/free \
  -H "Content-Type: application/json" \
  -d '{"birth":"1998-03-15","calendar":"solar","time":"14:30","gender":"female"}'
```

## 프로젝트 구조

```
src/
 ├ http/
 │   ├ routes/          REST 라우트 (DI 팩토리 패턴)
 │   ├ transformers/    SajuData → 표시용 DTO (영업 비밀 차단막)
 │   ├ schemas/         Zod 요청 스키마
 │   ├ middleware/      CORS 등
 │   └ errors.ts
 ├ db/client.ts         Prisma 싱글톤
 ├ lib/                 사주 계산 엔진 (수정 금지)
 ├ data/                정적 테이블 (수정 금지)
 ├ types/               공용 타입
 ├ utils/               공용 유틸
 └ server-rest.ts       서버 진입점

prisma/schema.prisma
docker-compose.yml
docs/                   내부 설계·레퍼런스 문서
tests/                  Jest 테스트
```

## 규칙

자세한 개발 규칙은 [`AGENTS.md`](AGENTS.md) (`CLAUDE.md` 심볼릭 링크) 참조. 요약:

- 사주 파이프라인 10단계 순서 수정 금지
- API 응답에 영업 비밀 필드(`wuxingCount`, `jiJangGan`, `tenGods`, `dayMasterStrength`, `gyeokGuk`, `yongSin` 등) 노출 금지 — 트랜스포머가 유일한 통로
- 무료 플로에서 LLM 호출 금지
- 개인정보(생년월일·출생시각·성별·출생지) 로그 출력 금지
- `eslint-disable`, `@ts-ignore` 사용 금지

## 라이선스

UNLICENSED (내부 프로젝트).

## 히스토리

이 레포는 [`fortuneteller`](https://github.com/hjsh200219/fortuneteller) MCP 서버의 사주 계산 엔진을 기반으로 포크되어 dohwa-backend REST 서비스로 전환되었다. MCP 관련 진입점·도구(`src/index.ts`, `src/server-http.ts`, `src/tools/`, `src/core/`, `smithery.yaml`, `railway.json` 등)는 제거되었으며 사주 계산 라이브러리(`src/lib/`, `src/data/`)는 원본 그대로 보존된다.
