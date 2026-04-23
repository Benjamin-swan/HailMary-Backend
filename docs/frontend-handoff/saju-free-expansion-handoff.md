# 프론트 핸드오프 — 무료 사주 응답 확장

> 도화선 프론트(`../dohwa_frontend`) 담당자(클로드/사람)에게 전달하는 브리프.
> 백엔드 PR "무료 사주 응답 확장"(exec-plan: `docs/exec-plans/active/saju-free-expansion.md`) 배포 이후 필요한 프론트 작업.
>
> **전달 시점**: 백엔드 구현 완료 후. 그 전엔 이 문서 내용이 계약 초안임.
> **백엔드 exec-plan**: `dohwa-backend/docs/exec-plans/active/saju-free-expansion.md` 전체 참고.

---

## 배경 요약 (세션이 초기화됐다면 이거부터 읽기)

도화선은 캐릭터(연우/도윤) 기반 **연예운 사주 서비스**. 구성:
- **프론트(너네)**: Next.js 앱, `../dohwa_frontend/`
- **백엔드**: hono + Prisma + MySQL 단일 프로세스, `../dohwa-backend/`, 포트 8000

현재 무료 사주(`POST /api/saju/free`) 응답은 4기둥 + 1줄 하이라이트만 내려옴. 사용자 테스트 결과 "경쟁사 대비 정보량 빈약" 피드백. 백엔드는 **명식 상세·대운·오행·용신·신강신약까지 응답에 포함**하도록 확장한다. 프론트는 이 정보를 렌더하는 UI를 5개 화면 정도로 추가 구현 필요.

**영업비밀 정책 재정의**: 기존 `backend-integration.md §9`는 `wuxingCount`/`tenGods`/`yongSin` 등을 "절대 노출 금지"로 규정했었음. 이건 **명리학 표준 계산 결과물**이라 공개 GitHub 사주 레포들에서도 다 공개되는 내용. 이번 기회에 정책을 "**표시용 결과는 공개, 알고리즘 선택 로직·해석 텍스트·유료 프롬프트만 보호**"로 재정의.

---

## 1. 새 응답 계약 (`POST /api/saju/free`)

### 요청 — 변경 없음

```json
{
  "birth": "1996-05-29",
  "calendar": "solar",
  "time": "16:12",
  "gender": "male"
}
```

### 응답 200 — 아래 필드 신규/확장 **모두 포함**됨

```jsonc
{
  "pillars": [
    {
      "label": "년주",
      "heaven": "丙",
      "earth": "子",
      "heavenHangul": "병",
      "earthHangul": "자",
      "element": "화 / 수",           // 기존
      "hue": "#E6A88E",               // 기존 (천간 오행 hex)
      "yinYang": {                    // 신규
        "heaven": "양",
        "earth": "양"
      },
      "tenGod": {                     // 신규 — 십성
        "heaven": "비견",
        "earth": "정관",
        "heavenHanja": "比肩",
        "earthHanja": "正官"
      },
      "twelvePhase": {                // 신규 — 십이운성
        "name": "태",
        "hanja": "胎"
      },
      "sinSals": [                    // 신규 — 기둥별 신살 배치
        { "slug": "do_hwa_sal", "label": "도화살", "hanja": "桃花殺" }
      ],
      "unknown": false                // 기존
    }
    // month/day/hour 동일 구조 (총 4개)
  ],

  "highlight": "화개살(華蓋殺) — 年支에 위치",     // 기존 유지

  "wuxing": {                         // 신규
    "counts":   { "목": 1, "화": 3, "토": 1, "금": 0, "수": 3 },
    "ratios":   { "목": 12.5, "화": 37.5, "토": 12.5, "금": 0.0, "수": 37.5 },
    "judgments":{ "목": "적정", "화": "과다", "토": "적정", "금": "결핍", "수": "발달" }
  },

  "yongSin": {                        // 신규 — 용신/희신/기신. 내부 yongSin 미산출 시 전체 null 가능
    "primary":  { "element": "수", "hanja": "水", "role": "용신" },
    "secondary": null,                //  ← 희신은 선택 — 내부 secondaryYongSin 없으면 null
    "opposing": { "element": "화", "hanja": "火", "role": "기신" }
  },

  "dayMaster": {                      // 신규 — 일간 + 신강신약
    "stem": "병",
    "stemHanja": "丙",
    "strengthLevel": "신강",          // 7단계 라벨
    "strengthScale": 7,               // 항상 7 (7단계 스케일임을 명시)
    "strengthPosition": 5             // 1=극약 ~ 7=극왕
  },

  "daeUn": {                          // 신규 — 대운표
    "startAge": 2,
    "direction": "forward",           // "forward" | "reverse" (순행/역행)
    "periods": [                      // 정확히 7개 (나이 2/12/22/32/42/52/62 식)
      {
        "age": 2,
        "startYear": 1998,             // 출생년(1996) + age(2) — 현재 관례
        "stem": "갑",
        "branch": "오",
        "stemHanja": "甲",
        "branchHanja": "午",
        "element": "목 / 화",
        "hue": "#9CC8B0"
      }
      // ... 총 7개
    ]
  },

  "sajuRequestId": "svr_01KPQ..."    // 기존 (유료 리포트용)
}
```

### 에러 — 변경 없음

```json
400 { "error": "BAD_REQUEST", "detail": [ZodIssue...] }
500 { "error": "CALCULATION_FAILED" }
```

---

## 2. 값 도메인 레퍼런스

**오행 5종 (한글 고정)**: `"목"` `"화"` `"토"` `"금"` `"수"`

**오행별 hex 컬러 (기존 팔레트 — 변경 없음)**:
```
목 → #9CC8B0
화 → #E6A88E
토 → #E6C58E
금 → #C5CAD4
수 → #6B8BB5
```

**십이운성 12단계 (`name` / `hanja`)**:
```
태(胎) · 양(養) · 장생(長生) · 목욕(沐浴) · 관대(冠帶) · 건록(建祿)
제왕(帝旺) · 쇠(衰) · 병(病) · 사(死) · 묘(墓) · 절(絕)
```

**십성 10종 (`name` / `hanja`)**:
```
비견(比肩) · 겁재(劫財) · 식신(食神) · 상관(傷官) · 편재(偏財)
정재(正財) · 편관(偏官) · 정관(正官) · 편인(偏印) · 정인(正印)
```

> **일주 천간 주의**: 일간(자기 자신) 대비 자기 자신의 십성 계산은 정의상 `"비견"` 이 되어 API 응답의 `pillars[2].tenGod.heaven` 은 항상 `"비견"` 으로 내려온다. UI 에서 일간을 "일간(日干)" 라벨로 띄우고 싶다면 `label === "일주"` 기둥의 heaven 슬롯을 프론트에서 교체 렌더하면 된다.

**신살 슬러그 — 타입 정의는 15종**이지만 **현재 백엔드가 실제로 판정·배치하는 것은 7종**:

```
실제 방출 (UI 매핑 필수):
  cheon_eul_gwi_in (천을귀인), do_hwa_sal (도화살), yeok_ma_sal (역마살),
  hwa_gae_sal (화개살), gong_mang (공망), won_jin_sal (원진살),
  gwi_mun_gwan_sal (귀문관살)

타입에는 있으나 현재 미방출 (findSinSals 확장 전엔 빈 배열로만 등장):
  cheon_deok_gwi_in, wol_deok_gwi_in, mun_chang_gwi_in, hak_dang_gwi_in,
  geum_yeo_rok, yang_in_sal, baek_ho_sal, gwa_suk_sal
```

응답 `pillars[*].sinSals[]` 는 각 기둥 지지에 실제로 걸린 것만 배열로 나옴. 한 기둥에 0~여러 개 가능. 전체 enum 은 `dohwa-backend/src/types/index.ts:168` 참조.

> **프론트 UI 권고**: 당장은 실제 방출 7종의 `slug → 한글 설명` 매핑만 있으면 충분. 나머지 8종은 `findSinSals` 가 확장되는 시점에 계약이 아니라 "데이터가 채워지기만" 하므로, 슬러그→설명 사전에 16종 전부 등록해두면 자동으로 커버됨.

**오행 판정 라벨 (개수 기반)**:
```
0개 → "결핍"
1개 → "적정"
2개 → "발달"
3개 이상 → "과다"
```
비율(`ratios`)도 함께 내려주니 자체 분류 커스터마이징 원하면 프론트에서 재계산 가능.

**신강신약 7단계** (`strengthPosition` 1~7):
```
1=극약 · 2=태약 · 3=신약 · 4=중화 · 5=신강 · 6=태강 · 7=극왕
```
`strengthLevel` 문자열과 `strengthPosition` 정수 둘 다 오니 편한 걸로 사용.

---

## 3. 해야 할 일

### (1) 타입 갱신 — `src/features/saju/types.ts`

기존 `SajuFreeResponse` 완전 교체. 아래 구조 그대로 반영:

```ts
export interface Pillar {
  label: "년주" | "월주" | "일주" | "시주";
  heaven: string;
  earth: string;
  heavenHangul: string;
  earthHangul: string;
  element: string;
  hue: string;
  yinYang: { heaven: "양" | "음"; earth: "양" | "음" };
  tenGod: {
    heaven: string;
    earth: string;
    heavenHanja: string;
    earthHanja: string;
  };
  twelvePhase: { name: string; hanja: string };
  sinSals: { slug: string; label: string; hanja: string }[];
  unknown: boolean;
}

export interface Wuxing {
  counts:    Record<"목"|"화"|"토"|"금"|"수", number>;
  ratios:    Record<"목"|"화"|"토"|"금"|"수", number>;
  judgments: Record<"목"|"화"|"토"|"금"|"수", "결핍"|"적정"|"발달"|"과다">;
}

export interface YongSinSlot {
  element: string;
  hanja: string;
  role: "용신" | "희신" | "기신";
}

export interface YongSinView {
  primary:   YongSinSlot;               // role="용신"
  secondary: YongSinSlot | null;        // role="희신" — 내부 secondaryYongSin 없으면 null
  opposing:  YongSinSlot;               // role="기신" — 용신의 상극 오행
}

export interface DayMaster {
  stem: string;
  stemHanja: string;
  strengthLevel: "극약"|"태약"|"신약"|"중화"|"신강"|"태강"|"극왕";
  strengthScale: 7;
  strengthPosition: 1|2|3|4|5|6|7;
}

export interface DaeUnPeriod {
  age: number;
  startYear: number;
  stem: string;
  branch: string;
  stemHanja: string;
  branchHanja: string;
  element: string;
  hue: string;
}

export interface DaeUn {
  startAge: number;
  direction: "forward" | "reverse";
  periods: DaeUnPeriod[];   // 길이 7 고정
}

export interface SajuFreeResponse {
  pillars: Pillar[];              // 길이 4 고정
  highlight: string;
  wuxing: Wuxing;
  yongSin: YongSinView | null;    // 내부 yongSin 부재 방어. 실제 운영에선 항상 채워짐
  dayMaster: DayMaster;
  daeUn: DaeUn;
  sajuRequestId: string;
}
```

### (2) UI 5개 화면 구현

참고 스크린샷은 사용자가 별도 제공. 경쟁사 형태 참고:

| 화면 | 주 데이터 | 참고 포인트 |
|---|---|---|
| 명식 상세표 | `pillars[*]` 의 십성·십이운성·신살·귀인 | 표 형태, 기둥당 세로 열, 한자 병기 |
| 대운표 | `daeUn.periods` | 7개 구간 가로 나열, 나이·년도·간지 |
| 오행 5각형 차트 | `wuxing.counts` | 목→화→토→금→수 꼭짓점 + 상생(청색 화살표) + 상극(적색 점선). 상생·상극은 오행 일반 지식이라 프론트 상수로 관리 |
| 오행 강약 막대 | `wuxing.counts` or `ratios` | 5개 막대, 가장 많은 오행 강조 |
| 용신·희신·기신 + 신강신약 | `yongSin`, `dayMaster`, `wuxing` | 비율 + 판정 + 용/희/기 원형 + 신강신약 게이지(7단계) |

상생(相生) 순환: 목→화→토→금→수→목
상극(相剋) 순환: 목→토→수→화→금→목

### (3) `docs/backend-integration.md` 갱신 (프론트 레포)

**§2 무료 사주 API 계약**: 응답 바디 섹션을 위 신규 JSON으로 교체.
**§9 보안 / 알고리즘 보호 원칙**: 아래 내용으로 개정.

```
## 9. 보안 / 알고리즘 보호 원칙 (2026-04 개정)

### 공개 OK — 명리학 표준 계산 결과물
- 4기둥(천간·지지·음양·오행)
- 십성, 십이운성, 신살(위치 포함)
- 오행 분포·비율·강약
- 용신·희신·기신
- 신강신약 단계
- 대운(7구간)

### 보호 대상 — 진짜 영업 비밀
- 용신 선택 알고리즘 근거 텍스트(`yongSin.reasoning` 내부 필드)
- 일간 강약 수치·판정 근거 텍스트(`score`, `analysis` 내부 필드)
- 격국 상세 판정(`gyeokGuk`)
- 지장간 세력 수치(`jiJangGan`)
- 지지 관계 판정(`branchRelations`)
- 월령 판정 근거(`wolRyeong.reason`)
- **PR3 유료 리포트의 Claude 프롬프트 원문·캐릭터 톤·해석 유파 가중치**

### 변함없는 원칙
- Claude API 키는 백엔드 전용
- 500 응답에 스택/내부 에러 노출 금지
- step3 자유 텍스트는 로그 출력 금지
```

---

## 4. 브레이킹 체인지 · 호환성

- **응답 shape이 확장**되므로 기존 타입은 **깨짐**. 전면 교체 작업 필요.
- 다만 기존 `pillars` / `highlight` / `sajuRequestId` 3개 최상위 필드는 **구조·의미 변경 없음** — 기존 화면은 그대로 작동. 새 필드(`wuxing`, `yongSin`, `dayMaster`, `daeUn`)만 추가 UI 필요.
- 사용자 배포 이전 구조 공존 기간 없음(단일 배포). 백엔드 머지 = 프론트 머지 동시 진행 권장.

---

## 5. 개발 시 확인 경로

- 로컬 백엔드 기동: `cd ../dohwa-backend && docker compose up -d mysql && npm run dev` → `http://localhost:8000`
- 스모크: 
  ```bash
  curl -X POST http://localhost:8000/api/saju/free \
    -H "Content-Type: application/json" \
    -d '{"birth":"1996-05-29","calendar":"solar","time":"16:12","gender":"male"}' | jq
  ```
- 백엔드 확정 계약 원본: `dohwa-backend/docs/references/rest-api.md` (백엔드 PR 머지 후 최신값 반영됨)
- 백엔드 exec-plan: `dohwa-backend/docs/exec-plans/active/saju-free-expansion.md`

---

## 6. 질문 생기면

- 슬러그 목록·내부 타입이 더 필요하면 `dohwa-backend/src/types/index.ts` 열어보면 됨
- 계산 결과 예시 필요하면 백엔드 스모크 커맨드로 생성 후 응답 JSON 참고
- 영업비밀 경계가 애매한 필드 발견하면 백엔드 담당과 논의 (필드명만 보고 공개 금지 판단하지 말 것 — 이번 개정으로 기존 "금지 목록"이 축소됐음)
