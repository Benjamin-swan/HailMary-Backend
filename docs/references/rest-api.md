# REST API — dohwa-backend

프론트엔드(`dohwa_frontend`) 가 소비하는 HTTP 엔드포인트 명세.
**계약 원본**: `dohwa_frontend/docs/backend-integration.md` (프론트·백 단일 소스).

## 공통

| 항목 | 값 |
|---|---|
| 베이스 URL (로컬) | `http://localhost:8000` |
| Content-Type | `application/json; charset=utf-8` |
| CORS | 환경변수 `CORS_ORIGINS` 콤마 분리 |
| 응답 언어 | 한국어 (에러 코드는 영문 상수) |

## GET `/health`

헬스체크. 인프라 모니터링용.

응답 200:
```json
{ "status": "ok" }
```

---

## POST `/api/saju/free`

무료 사주 계산.

### 요청

```json
{
  "birth": "1998-03-15",
  "calendar": "solar",
  "time": "14:30",
  "gender": "female"
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| `birth` | string | ISO `YYYY-MM-DD`. 1900–2200 범위 |
| `calendar` | `"solar"` \| `"lunar"` | 양력/음력 |
| `time` | string \| `"unknown"` | `"HH:MM"` 또는 `"unknown"` |
| `gender` | `"male"` \| `"female"` | 성별 |

주의:
- `name`, `birthCity` 는 **받지 않음**. 서버는 `birthCity = "서울"` 고정.
- `birth` 점 구분자(`.`)는 프론트에서 ISO 로 변환해 전송.

### 성공 응답 (200)

```json
{
  "pillars": [
    {
      "label": "년주",
      "heaven": "戊", "earth": "寅",
      "heavenHangul": "무", "earthHangul": "인",
      "element": "토 / 목",
      "hue": "#E6C58E",
      "yinYang": { "heaven": "양", "earth": "양" },
      "tenGod": { "heaven": "편재", "earth": "비견", "heavenHanja": "偏財", "earthHanja": "比肩" },
      "twelvePhase": { "name": "건록", "hanja": "建祿" },
      "sinSals": [],
      "unknown": false
    }
    // 월주·일주·시주 동일 구조 (생략)
  ],
  "highlight": "도화살(桃花殺) — 日支에 위치",
  "wuxing": {
    "counts":    { "목": 3, "화": 1, "토": 2, "금": 1, "수": 0 },
    "ratios":    { "목": 42.9, "화": 14.3, "토": 28.6, "금": 14.3, "수": 0 },
    "judgments": { "목": "과다", "화": "적정", "토": "발달", "금": "적정", "수": "결핍" }
  },
  "yongSin": {
    "primary":   { "element": "수", "hanja": "水", "role": "용신" },
    "secondary": { "element": "금", "hanja": "金", "role": "희신" },
    "opposing":  { "element": "화", "hanja": "火", "role": "기신" }
  },
  "dayMaster": {
    "stem": "갑",
    "stemHanja": "甲",
    "strengthLevel": "신강",
    "strengthScale": 7,
    "strengthPosition": 5
  },
  "daeUn": {
    "startAge": 2,
    "direction": "reverse",
    "periods": [
      {
        "age": 2, "startYear": 2000,
        "stem": "갑", "branch": "오",
        "stemHanja": "甲", "branchHanja": "午",
        "element": "목 / 화", "hue": "#9CC8B0"
      }
      // 총 7구간 (생략)
    ]
  },
  "sajuRequestId": "svr_01HXY..."
}
```

| 최상위 필드 | 타입 | 설명 |
|---|---|---|
| `pillars` | Array(length=4) | 년주/월주/일주/시주 순서 고정 |
| `highlight` | string | 연애운 포커스 신살 1개 요약 |
| `wuxing` | object | 오행 counts/ratios(%)/judgments |
| `yongSin` | object \| null | 용신/희신/기신 (oldest style; `secondary` 는 null 가능) |
| `dayMaster` | object | 일간 + 신강신약 7단계 |
| `daeUn` | object | 대운 시작 나이·방향·구간 7개 배열 |
| `sajuRequestId` | string | `svr_` prefix + ULID. 유료 리포트 단계에서 재계산 회피용 |

#### `pillars[]` 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `label` | `"년주"` \| `"월주"` \| `"일주"` \| `"시주"` | |
| `heaven` / `earth` | string | 천간·지지 **한자** 1자 (unknown 시 `"?"`) |
| `heavenHangul` / `earthHangul` | string | 천간·지지 **한글** 1자 (unknown 시 `"?"`) |
| `element` | string | `"천간오행 / 지지오행"` (한글). unknown 시 `"—"` |
| `hue` | string | hex 컬러 (천간 오행 기준). unknown 시 `"—"` |
| `yinYang` | `{heaven, earth}` | 음양 (`"양"` \| `"음"`) |
| `tenGod` | `{heaven, earth, heavenHanja, earthHanja}` | 십성(한글 + 한자) |
| `twelvePhase` | `{name, hanja}` | 십이운성 단계 (한글 + 한자) |
| `sinSals` | Array | 이 기둥 지지에 놓인 신살 목록. 각 원소 `{slug, label, hanja}` |
| `unknown` | boolean | 시주 unknown 플래그 |

#### `wuxing` 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `counts` | Record\<오행, number\> | 8자 중 해당 오행 개수 |
| `ratios` | Record\<오행, number\> | 퍼센트, 소수 1자리 |
| `judgments` | Record\<오행, string\> | `결핍`(0) \| `적정`(1) \| `발달`(2) \| `과다`(3+) |

#### `dayMaster` 필드

| 필드 | 값 범위 |
|---|---|
| `strengthLevel` | `극약`, `태약`, `신약`, `중화`, `신강`, `태강`, `극왕` |
| `strengthScale` | 고정 `7` |
| `strengthPosition` | 1~7 (1=극약, 7=극왕) |

#### `daeUn` 필드

- `direction`: `"forward"`(순행: 양남·음녀) \| `"reverse"`(역행: 음남·양녀)
- `periods`: 길이 고정 **7**. 각 원소 `{age, startYear, stem, branch, stemHanja, branchHanja, element, hue}`

오행 hue 팔레트:

| 오행 | hex |
|---|---|
| 목 | `#9CC8B0` |
| 화 | `#E6A88E` |
| 토 | `#E6C58E` |
| 금 | `#C5CAD4` |
| 수 | `#6B8BB5` |

### 에러

400 BAD_REQUEST:
```json
{
  "error": "BAD_REQUEST",
  "detail": [
    { "path": ["birth"], "message": "birth must be YYYY-MM-DD" }
  ]
}
```

500 CALCULATION_FAILED:
```json
{ "error": "CALCULATION_FAILED" }
```

500 응답에는 내부 에러 메시지/스택이 **절대** 포함되지 않는다. 서버 로그에는 풀 스택이 남는다.

### curl 예시

```bash
curl -X POST http://localhost:8000/api/saju/free \
  -H "Content-Type: application/json" \
  -d '{"birth":"1998-03-15","calendar":"solar","time":"14:30","gender":"female"}'
```

### 응답에 **절대** 포함되지 않는 내부 필드

다음 필드 이름·텍스트는 응답 본문에 등장하지 않는다 (영업 비밀 — 자세한 정책은 `docs/SECURITY.md` 참조):

- 내부 원본 객체명: `wuxingCount`, `jiJangGan`, `tenGodsDistribution`, `dayMasterStrength`, `gyeokGuk`, `branchRelations`, `wolRyeong`, `dominantElements`, `weakElements`, `specialMarks`, `stemElement`, `branchElement`.
- 판정 근거·수치 텍스트: `reasoning` (용신 근거), `analysis` / `score` (신강신약 근거/점수).

노출되는 `yongSin`·`dayMaster`·`wuxing` 는 **파생 DTO** 이며 위 원본 객체와는 다른 구조·키다.

---

## POST `/api/saju/survey`

사용자 설문 응답 저장. 무료/유료 무관하게 수집되며, 향후 유료 리포트(`/api/reading/premium`) 생성 시 Claude 프롬프트 컨텍스트로 쓰인다.

**설계 원칙**: 백엔드는 선택지의 의미를 모름. 구조(길이·개수·포맷)만 검증하고 **슬러그 문자열을 그대로 저장**한다. 문항/선택지가 바뀌면 프론트가 `surveyVersion` 을 올리면 되고, 백엔드 코드는 불변.

### 요청

```json
{
  "sajuRequestId": "svr_01KPQ...",
  "surveyVersion": "v1",
  "step1": ["waiting_new", "dating"],
  "step2": ["destined", "timing"],
  "step3": "요즘 고민하는 내용..."
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| `sajuRequestId` | string | `POST /api/saju/free` 응답으로 받은 ID. 정규식 `^svr_[0-9A-Z]{26}$` |
| `surveyVersion` | string | 프론트의 설문 버전 태그. `[a-z0-9_.-]+`, 1~16자. 현재 `"v1"` |
| `step1` | string[] | 상황 선택지 슬러그 배열. 최대 10개, 각 원소 1~48자 |
| `step2` | string[] | 관심사 선택지 슬러그 배열. 제약 동일 |
| `step3` | string \| null | 자유 텍스트(고민). 최대 100자. 생략/`null`/trim 후 빈 문자열은 null 로 저장 |

**재제출**: 같은 `sajuRequestId` 로 POST 시 기존 row 덮어쓰기(upsert). "최근 row 고르기" 패턴 원천 차단.

**슬러그 카탈로그**: 버전별 키 목록 해석은 프론트 계약(`dohwa_frontend/docs/backend-integration.md`) 참조. 백엔드는 구조 검증만.

### 성공 응답 (200)

```json
{ "ok": true }
```

### 에러

400 BAD_REQUEST (Zod 검증 실패):
```json
{ "error": "BAD_REQUEST", "detail": [{ "path": ["sajuRequestId"], "message": "..." }] }
```

404 NOT_FOUND (sajuRequestId 가 DB 에 없음):
```json
{ "error": "NOT_FOUND", "detail": { "entity": "sajuRequest" } }
```

500 INTERNAL_ERROR:
```json
{ "error": "INTERNAL_ERROR" }
```

### curl 예시

```bash
# 먼저 무료 사주로 sajuRequestId 받기
SID=$(curl -sS -X POST http://localhost:8000/api/saju/free \
  -H "Content-Type: application/json" \
  -d '{"birth":"1995-07-22","time":"09:15","calendar":"solar","gender":"female"}' \
  | jq -r .sajuRequestId)

# 설문 전송
curl -X POST http://localhost:8000/api/saju/survey \
  -H "Content-Type: application/json" \
  -d "{\"sajuRequestId\":\"$SID\",\"surveyVersion\":\"v1\",
       \"step1\":[\"waiting_new\"],\"step2\":[\"destined\"],
       \"step3\":\"짧은 고민\"}"
```
