# PR2 — 무료 사주 응답 확장 (명식 상세·대운·오행·용신·신강신약)

> 주의: PR 번호는 작업 순서상 PR2 이지만, 제품 플로의 "PR2 결제"와 별개 PR 이다. 결제·Claude 보다 먼저 들어갈 수 있어 이 계획서에서는 **무료 사주 확장 PR**로만 지칭.

## Context

현재 무료 사주 응답(`/api/saju/free`)은 **4기둥 + highlight 1줄 + sajuRequestId**만 내보내는 미니멀 구조. 사용자 테스트 결과 "경쟁사 대비 정보량 빈약" 피드백. 스크린샷 기준 타 서비스 무료 티어는 다음을 제공:

- 명식 상세표: 십성·십이운성·신살·귀인
- 대운표(10년 주기 7~12구간)
- 오행 분포·비율·강약 차트
- 용신·희신·기신
- 신강신약 7단계 게이지

우리 계산 엔진은 **이 정보 대부분을 이미 계산 중** (`SajuData`). 지금까지는 "영업 비밀" 정책으로 응답에서 차단해왔음. 재검토 결과:

- 이 정보들은 사주 명리학 **표준 계산 결과**이며 공개 GitHub 레포(`sajuapi`, `pycheonmun` 등)에서도 로직 포함 공개됨
- 도화선의 실질 차별점은 **캐릭터별(doyoon/yeonwoo) Claude 해석**(PR3)에 있음
- 기초 데이터는 공개하고, 해석·알고리즘 선택 로직은 보호하는 선이 업계 표준

**제품 효과**: 무료 티어 기대치 충족 → 이탈 감소 → 유료 해석 궁금증으로 전환 유인 상승.

## 범위 (명시)

포함:
- 정책 문서 개정 (`CLAUDE.md`, `backend-integration.md`, `docs/SECURITY.md`)
- 새 lib 모듈: `src/lib/twelve_phases.ts` (십이운성, 10천간×12지지 테이블 룩업)
- 기신(忌神) 계산 유틸 (용신의 상극 오행 역산)
- 오행 비율·과다결핍 판정 임계값 매핑
- 신강신약 5→7단계 매핑
- 트랜스포머 확장: 명식 상세, 대운, 오행, 용신, 신강신약
- 응답 Zod 스키마·DTO 타입·테스트
- 라이브 스모크 + 프론트 계약 문서 갱신

제외 (별도 PR):
- 프론트 UI 구현 — 백엔드 계약 확정 후 프론트 담당
- `/api/reading/premium` (유료 리포트) — 별도 PR3
- 결제 연동 (페이앱) — 별도 PR
- 궁합·직업 추천 등 기타 계산 결과 노출 (scope creep 방지)

## 정책 개정 — 영업비밀 라인 재정의

### 현 정책 (수정 대상)

`CLAUDE.md` Core Rule #6:
> **API 응답에 영업 비밀 필드 노출 금지** — `wuxingCount` / `jiJangGan` / `tenGods` / `tenGodsDistribution` / `dayMasterStrength` / `gyeokGuk` / `yongSin` / `branchRelations` / `sinSals`(배열) / `dominantElements` / `weakElements` / `specialMarks` / `stemElement` / `branchElement` / `yinYang` 등.

### 개정 방향

**공개 OK** (표시용 계산 결과 — 명리학 표준):
- 4기둥 천간·지지·음양·오행 (`stemElement`, `branchElement`, `yinYang`)
- 오행 분포 개수·비율 (`wuxingCount` 파생)
- 십성 배열 (`tenGods`) — 한자·한글 라벨 붙여서
- 십이운성 (신규 계산)
- 신살 배열 전체 (`sinSals`) — 위치 한자까지
- 용신·희신·기신 (`yongSin` 파생)
- 신강신약 단계 (`dayMasterStrength.level` 7단계 매핑)
- 대운 배열 (`daeUn`)

**보호 유지** (진짜 영업 비밀):
- `yongSin.reasoning` — 용신 선택 근거 텍스트 (어느 알고리즘을 어떻게 조합했는지 단서)
- `dayMasterStrength.score` / `dayMasterStrength.analysis` — 수치·근거 텍스트
- `gyeokGuk` 세부 — 격국 판정 기준 노출 위험
- `jiJangGan` 세부 세력 수치 — 판정 가중치 힌트
- `branchRelations` 상세 — 삼합/삼형/육해 판정 로직
- `wolRyeong` (득령 판정 근거 reason)
- **PR3 Claude 프롬프트 원문·캐릭터 톤 설정·해석 텍스트**
- **유파별 가중치**(`school_interpreter` 내부 설정)

### 개정할 문서

1. `CLAUDE.md` Core Rule #6 — 위 이분법으로 교체
2. `../dohwa_frontend/docs/backend-integration.md` §9 "보안 / 알고리즘 보호 원칙" — 갱신 요청(프론트 PR)
3. `docs/SECURITY.md` — 상세 근거 문서
4. `ARCHITECTURE.md` / `docs/ARCHITECTURE.md` 의 "영업 비밀 차단막" 섹션 — 새 경계 반영

## 확정 응답 계약 (제안)

### 요청 — 변경 없음

```json
POST /api/saju/free
{ "birth": "YYYY-MM-DD", "calendar": "solar"|"lunar", "time": "HH:MM"|"unknown", "gender": "male"|"female" }
```

### 응답 200 (신규 필드 포함)

```json
{
  "pillars": [
    {
      "label": "년주",
      "heaven": "丙", "earth": "子",
      "heavenHangul": "병", "earthHangul": "자",
      "element": "화 / 수",
      "hue": "#E6A88E",
      "yinYang": { "heaven": "양", "earth": "양" },
      "tenGod": { "heaven": "비견", "earth": "정관", "heavenHanja": "比肩", "earthHanja": "正官" },
      "twelvePhase": { "name": "태", "hanja": "胎" },
      "sinSals": [
        { "slug": "jae_sal", "label": "재살", "hanja": "災殺" }
      ],
      "unknown": false
    },
    ...  // 월주/일주/시주 동일 구조
  ],

  "highlight": "화개살(華蓋殺) — 年支에 위치",   // 기존 유지

  "wuxing": {
    "counts":   { "목": 1, "화": 3, "토": 1, "금": 0, "수": 3 },
    "ratios":   { "목": 12.5, "화": 37.5, "토": 12.5, "금": 0, "수": 37.5 },   // % 소수 1자리
    "judgments":{ "목": "적정", "화": "과다", "토": "적정", "금": "결핍", "수": "발달" }
  },

  "yongSin": {
    "primary":  { "element": "수", "hanja": "水", "role": "용신" },
    "secondary":{ "element": "금", "hanja": "金", "role": "희신" },
    "opposing": { "element": "화", "hanja": "火", "role": "기신" }
  },

  "dayMaster": {
    "stem": "병",
    "stemHanja": "丙",
    "strengthLevel": "신강",           // 7단계 라벨
    "strengthScale": 7,
    "strengthPosition": 5              // 7단계 중 5번째(1=극약, 7=극왕)
  },

  "daeUn": {
    "startAge": 2,
    "direction": "forward",            // forward | reverse (순행/역행)
    "periods": [
      { "age": 2,  "startYear": 1997, "stem": "갑", "branch": "오",
        "stemHanja": "甲", "branchHanja": "午",
        "element": "목 / 화", "hue": "#9CC8B0" },
      ... // 최대 10구간까지 (현재는 가변 — 결정 필요 참조)
    ]
  },

  "sajuRequestId": "svr_01KPQ..."
}
```

### 에러 — 변경 없음

400 `BAD_REQUEST`, 500 `CALCULATION_FAILED`

## 새 모듈 — `src/lib/twelve_phases.ts`

입력: `dayStem`, `branch`
출력: 12운성 단계 중 하나 (`'tae'|'yang'|'jangsaeng'|'mokyok'|'gwandae'|'geonrok'|'jewang'|'soe'|'byeong'|'sa'|'myo'|'jeol'`)

구현: 10천간 × 12지지 = 120 조합 룩업 테이블. 공개된 표준 대조표 인용 (만세력 기준).

```typescript
// 예시 시그니처
export type TwelvePhase =
  | 'tae' | 'yang' | 'jangsaeng' | 'mokyok'
  | 'gwandae' | 'geonrok' | 'jewang' | 'soe'
  | 'byeong' | 'sa' | 'myo' | 'jeol';

export function getTwelvePhase(dayStem: HeavenlyStem, branch: EarthlyBranch): TwelvePhase;

export const TWELVE_PHASE_LABEL: Record<TwelvePhase, { name: string; hanja: string }>;
```

## 기신(忌神) 계산 룰

```
기신 = 용신(yongSin.primaryYongSin)이 극(剋)하는 오행

오행 상극 관계:
  목 극 토, 토 극 수, 수 극 화, 화 극 금, 금 극 목

예: 용신이 수 → 기신은 화
    용신이 화 → 기신은 금
```

구현: `src/http/transformers/yongSinView.ts`에 작은 룩업 함수. `src/data/wuxing.ts`의 상극 관계 테이블 재사용.

## 신강신약 7단계 매핑

경쟁사 7단계(라벨 기준):
`극약 → 태약 → 신약 → 중화 → 신강 → 태강 → 극왕`

우리 내부 `dayMasterStrength.level` 5단계 + `score`(0-100 수치)로 7단계 재매핑:

| 내부 level | 내부 score 범위 | 노출 7단계 라벨 | position |
|---|---|---|---|
| very_weak | 0-15 | 극약 | 1 |
| very_weak | 16-25 | 태약 | 2 |
| weak | 26-40 | 신약 | 3 |
| medium | 41-60 | 중화 | 4 |
| strong | 61-75 | 신강 | 5 |
| very_strong | 76-90 | 태강 | 6 |
| very_strong | 91-100 | 극왕 | 7 |

**결정 필요**: 이 임계값이 적절한지 도메인 전문가(사용자) 리뷰 필요. 일단 제안값으로 시작.

## 오행 과다/결핍/적정 판정

개수 기준 간단 임계값:

| 개수 | 판정 |
|---|---|
| 0 | 결핍 |
| 1 | 적정 |
| 2 | 발달 |
| 3 이상 | 과다 |

**결정 필요**: 경쟁사 스크린샷 기준 `13.6%=적정`, `45.5%=과다`, `27.3%=발달`. 비율 기반이 더 정확할 수도. 일단 개수 기반으로 단순화 제안.

## 대운 개수 정책

`dae_un.ts`는 최대 12구간까지 계산 가능하나, 경쟁사는 7개 노출. 제안:

- 응답에 **10구간까지** 내보내기 (2세~92세 커버)
- 프론트가 노출 개수 결정 (7개든 12개든 슬라이스)

**결정 필요**: 10개 OK? 아니면 경쟁사 맞춰 7개?

## 파일 구조

```
src/lib/
 └ twelve_phases.ts              # 신규

src/http/
 ├ schemas/
 │   └ freeSaju.ts               # 변경 없음 (요청 스키마 그대로)
 ├ transformers/
 │   ├ hueMap.ts                 # 기존
 │   ├ pillarView.ts             # 확장 — tenGod/twelvePhase/sinSals 추가
 │   ├ sinSalPosition.ts         # 기존 (highlight 전용 유지)
 │   ├ pillarSinSals.ts          # 신규 — 기둥별 신살 배치
 │   ├ tenGodView.ts             # 신규 — 십성 라벨 한자 매핑
 │   ├ wuxingView.ts             # 신규 — 개수→비율·판정
 │   ├ yongSinView.ts            # 신규 — 용신/희신/기신
 │   ├ dayMasterView.ts          # 신규 — 신강신약 7단계 매핑
 │   ├ daeUnView.ts              # 신규 — 대운 배열 변환
 │   └ sajuDisplay.ts            # 상위 조립자 — 위 트랜스포머들 병합
 └ routes/freeSaju.ts            # 변경 최소 (sajuDisplay 호출만)

src/data/
 └ twelve_phases_table.ts        # 신규 — 10천간×12지지 룩업

tests/http/
 └ transformers.test.ts          # 대폭 확장 (각 신규 뷰별)

docs/
 ├ references/rest-api.md        # 응답 예시 교체
 └ SECURITY.md                   # 영업비밀 정책 개정

CLAUDE.md                        # Core Rule #6 개정
ARCHITECTURE.md
docs/ARCHITECTURE.md
```

## 테스트 범위

- `twelve_phases.getTwelvePhase()` — 대표 12쌍 케이스 (甲子=목욕, 병인=장생 등)
- `pillarView` — 확장된 필드 스냅샷 (십성·12운성·신살 배치)
- `wuxingView` — 비율 계산 정확성, 판정 매핑
- `yongSinView` — 용신·희신·기신 5 오행 순환 검증
- `dayMasterView` — 7단계 매핑 경계값 테스트
- `daeUnView` — 순행/역행 케이스
- 응답 **key set 회귀 테스트 갱신** — 기존 "영업 비밀 미노출" 테스트를 새 정책에 맞춰 갱신
  - 여전히 금지: `reasoning`, `analysis`, `score`, `gyeokGuk`, `jiJangGan`, `branchRelations`, `wolRyeong`
  - 새로 허용: `wuxing`, `yongSin`, `dayMaster.strengthLevel`, `tenGod`, `twelvePhase`

## 완료 정의

1. `npm run lint` 0 errors
2. `npm test` 전부 통과 (기존 168 + 신규 ~30~40개)
3. `CLAUDE.md` Core Rule #6 개정 반영
4. 라이브 스모크: `curl /api/saju/free` 응답에 신규 필드 전부 채워서 내려옴
5. 영업비밀 필드 grep 0건 (`reasoning`, `gyeokGuk.description`, `wolRyeong`, `jiJangGan` 등)
6. `docs/references/rest-api.md` 응답 예시 실제 값으로 교체
7. `backend-integration.md` 갱신 요청 사항 목록화 (프론트 PR로 전달)
8. Core Rule #1 (saju.ts 미수정) 준수 — twelve_phases는 `lib`에 신규 추가일 뿐

## 확정 결정 (2026-04-21)

1. **신강신약 7단계 임계값** — 위 매핑표 제안값 그대로 시작. 실운영 데이터 수집 후 필요 시 조정.
2. **오행 과다/결핍 판정** — **개수 기반** (0=결핍, 1=적정, 2=발달, 3+=과다). 단순성 우선, 비율은 `wuxing.ratios` 필드로 별도 제공하므로 프론트에서 원하면 직접 재판정 가능.
3. **대운 노출 개수** — **7구간** (경쟁사 규격). 배열 `daeUn.periods.length === 7` 고정.
4. **PR 순서** — 본 PR을 **PR2(페이앱) 앞에 배치**. 무료 티어 완성도가 유료 전환 유인의 선행 조건.
5. **프론트 UI** — 별도 세션에서 별도 PR. 본 PR은 백엔드 계약 확정까지만 책임. 프론트 핸드오프 문서는 `docs/frontend-handoff/saju-free-expansion-handoff.md`로 작성 후 전달.

## 의존·후속

- 선행: 없음. 현재 상태에서 즉시 착수 가능.
- 후속:
  - 프론트 UI 구현 PR (도화선 프론트 레포)
  - `backend-integration.md` §9 보안 원칙 갱신 PR (도화선 프론트 레포)
  - PR2(페이앱), PR3(Claude 유료 리포트)는 본 PR과 독립 — 순서 자유
