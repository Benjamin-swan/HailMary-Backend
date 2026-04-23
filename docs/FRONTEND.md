# Frontend / Interface

> dohwa-backend 는 REST API 서비스이다. 자체 UI 가 없으며, 자매 프로젝트 `dohwa_frontend` (Next.js) 가 이 API 를 소비한다.

## 공통 원칙

- **계약 단일 소스**: [`../dohwa_frontend/docs/backend-integration.md`](../../dohwa_frontend/docs/backend-integration.md). 백/프론트 양측이 이 문서를 기준으로 동작한다. 변경 시 두 레포 모두에 반영.
- **영업 비밀 보호**: API 응답은 오직 표시용(display-ready) 데이터만 포함. 사주 알고리즘의 내부 산출물(`wuxingCount` / `jiJangGan` / `tenGods` / `dayMasterStrength` / `gyeokGuk` / `yongSin` 등)은 **절대 응답에 포함되지 않음**. 트랜스포머 레이어(`src/http/transformers/`)가 유일한 통로.
- **비용 게이트**: 무료 플로는 `calculateSaju` 결과 + 하드코딩 전개 멘트만. LLM 호출은 결제 검증 완료된 유료 플로에서만 (유료 플로는 별도 PR).

## REST 엔드포인트 목록

| Method | Path | 상태 | 용도 |
|---|---|---|---|
| GET | `/health` | ✅ 구현 | 헬스체크 |
| POST | `/api/saju/free` | ✅ 구현 | 무료 사주 계산 |
| POST | `/api/payment/prepare` | ⏳ 예정 | 페이앱 결제 생성 |
| POST | `/api/payment/webhook` | ⏳ 예정 | 페이앱 결제 검증 수신 |
| POST | `/api/reading/premium` | ⏳ 예정 | 유료 캐릭터 리포트 (Claude API) |

엔드포인트별 상세 요청/응답 스키마는 [`references/rest-api.md`](references/rest-api.md) 참조.

## 인증 · 인가

현재 구현된 엔드포인트(`/api/saju/free`)는 **인증 불필요**. 누구나 호출 가능하며 rate limit 은 별도 PR 에서 도입 예정.

유료 엔드포인트(`/api/reading/premium`)는 결제 검증 완료 토큰을 요구한다. 설계는 결제 연동 PR 에서 확정.

## CORS

`CORS_ORIGINS` 환경변수 (콤마 분리) 기반. 프로덕션에서는 도메인 정확 매칭만 허용 (와일드카드 금지).

## 프론트 측 대응

프론트 작업 체크리스트는 [`../dohwa_frontend/docs/backend-integration.md`](../../dohwa_frontend/docs/backend-integration.md) §11 참조.

## 히스토리

이 파일은 원본 fortuneteller MCP 서버의 인터페이스 문서였다. dohwa-backend 로 전환되면서 MCP 관련 내용은 제거되고 REST API 서비스 기준으로 다시 작성되었다.
