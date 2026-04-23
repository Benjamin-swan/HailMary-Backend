# 배우자 얼굴 이미지 20종 — 제작 가이드 & 프롬프트

> 도화선 무료·유료 연애운 리포트의 "미래 연인 얼굴" 이미지 세트.
> 무료: 블러 처리되어 노출 / 유료: 블러 해제되어 노출.
> 사주 엔진의 **배우자궁(일지) + 재성/관성 오행 + 음양** 조합으로 20개 슬롯 중 1개가 매칭된다.

---

## 1. 오행 × 음양 디자인 매트릭스

모든 프롬프트는 아래 표를 공통 설계 기준으로 삼는다. 20장이 "같은 시리즈"로 보이려면 이 표의 톤을 일관되게 유지하는 것이 가장 중요하다.

| 오행 | 코어 디스크립터                                 | 양 변조          | 음 변조            |
| ---- | ----------------------------------------------- | ---------------- | ------------------ |
| 木   | 키 크고 마른 체형, 시원한 이목구비, 초록 액센트 | 시원시원·활기    | 섬세·단아          |
| 火   | 또렷한 눈매, 선명한 입매, 따뜻한 톤             | 밝고 활기찬 웃음 | 은은히 빛나는 미소 |
| 土   | 둥근 인상, 안정적 체형, 포근한 톤               | 듬직·신뢰감      | 포근·편안          |
| 金   | 각진 선, 맑고 흰 피부, 단정                     | 단단·카리스마    | 차분·지적          |
| 水   | 부드러운 라인, 깊은 눈, 푸른/검은 톤            | 깊고 성숙        | 몽환적·여림        |

---

## 2. 파일명 규칙 (엄수)

백엔드 `slotId` 와 **1:1 동일**해야 한다. 한 글자라도 다르면 프론트에서 404.

```
{gender}-{element}-{yinyang}.webp
```

| 자리    | 허용값 (이 외 금지)                           |
| ------- | --------------------------------------------- |
| gender  | `m` · `f`                                     |
| element | `wood` · `fire` · `earth` · `metal` · `water` |
| yinyang | `yang` · `yin`                                |

- **모두 소문자**, 구분자는 하이픈 `-` 고정 (언더바·점 금지)
- 확장자 `.webp` 통일
- 예: `m-wood-yang.webp`, `f-water-yin.webp`

### 호스팅 경로

```
/images/spouse/{filename}
예) https://cdn.dohwa.app/images/spouse/m-wood-yang.webp
```

---

## 3. 납품 규격 공통

모든 20장이 같은 "세트"로 보여야 하므로 아래 규격을 동일하게 지킨다.

- **비율**: 3:4 세로 포트레이트
- **해상도**: 최소 1024 × 1365 (레티나 대응)
- **포맷**: `.webp`
- **구도**: 상반신 정면, 센터 구도, 얼굴이 상단 1/3 지점
- **배경**: 중립 톤 단색 또는 부드러운 그라데이션 (장면 배경·소품 금지)
- **조명 방향**: **왼쪽 45° 자연광** — 20장 전부 동일
- **연령대**: 20대 중반, 한국인 외모
- **피해야 할 요소**: 과한 메이크업, 한복·전통 의상, 화려한 액세서리, 강한 필터, 만화/일러스트 느낌
- **지향**: "실존 인물 같은 편안한 에디토리얼 포트레이트"

### 제작 방식

- 슬롯당 **5~10컷** 배치 생성 → 시리즈 톤에 가장 잘 맞는 1장 셀렉션
- 블러 처리는 **프론트엔드에서 CSS `filter: blur(Npx)` 로 처리** → 이미지 담당분은 원본 20장만 납품

---

## 4. 공통 프롬프트 베이스

모든 20개 프롬프트에 아래 요소가 공통으로 들어있다 (반복 서술되어 있음).

```
Korean, mid-20s, upper-body portrait, centered composition,
natural diffused lighting, photorealistic editorial style,
subtle film grain, shot on 85mm f/2, shallow depth of field,
clean natural skin texture, --ar 3:4 --style raw --v 6
```

---

## 5. 프롬프트 20종

### 5.1 남성 10장 (사용자가 여성일 때 매칭)

#### `m-wood-yang.webp` — 시원시원한 큰 나무

```
Korean man, mid-20s, tall lean build, long limbs, high cheekbones, sharp clean features, fresh open expression, confident direct gaze, subtle smile, moss-green linen shirt, bright crisp natural window light, upper-body portrait, centered, soft neutral beige-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-wood-yin.webp` — 섬세한 대나무

```
Korean man, mid-20s, tall slender build, delicate refined features, gentle thoughtful eyes, slightly averted contemplative gaze, soft neutral expression, sage-green knit sweater, soft diffused side light, upper-body portrait, centered, soft neutral beige-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-fire-yang.webp` — 태양 같은 활기

```
Korean man, mid-20s, athletic build, defined sharp eyes, bright warm smile, radiant confident energy, direct engaging gaze, warm coral-red henley shirt, warm golden natural light, upper-body portrait, centered, soft neutral warm-beige gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-fire-yin.webp` — 은은한 촛불

```
Korean man, mid-20s, slim build, defined eyes with soft warmth, gentle half-smile, warm expressive presence, soft engaging gaze, muted terracotta cashmere sweater, warm soft candle-like lighting, upper-body portrait, centered, soft neutral warm-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-earth-yang.webp` — 듬직한 산

```
Korean man, mid-20s, sturdy broad-shouldered build, round gentle face, kind steady eyes, warm reassuring smile, trustworthy calm presence, direct warm gaze, earth-tone ochre wool cardigan, warm even natural light, upper-body portrait, centered, soft neutral warm-tan gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-earth-yin.webp` — 포근한 흙

```
Korean man, mid-20s, gentle rounded build, soft warm face, kind thoughtful eyes, subtle soft smile, calm grounded presence, soft slightly downward gaze, warm beige cotton knit, soft muted natural light, upper-body portrait, centered, soft neutral warm-taupe gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-metal-yang.webp` — 단단한 칼

```
Korean man, mid-20s, lean defined build, sharp angular jawline, clear porcelain skin, crisp refined features, confident composed direct gaze, subtle assertive expression, charcoal tailored wool coat over white shirt, crisp bright lighting, upper-body portrait, centered, soft neutral cool-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-metal-yin.webp` — 차분한 은

```
Korean man, mid-20s, clean-lined build, refined angular features, clear pale skin, calm intelligent eyes, quiet composed expression, soft thoughtful gaze, ivory cashmere turtleneck, cool soft diffused lighting, upper-body portrait, centered, soft neutral silver-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-water-yang.webp` — 깊은 바다

```
Korean man, mid-20s, smooth flowing build, soft defined features, deep dark expressive eyes, mature contemplative presence, steady knowing gaze, navy cotton shirt, cool atmospheric lighting with subtle rim light, upper-body portrait, centered, soft neutral deep-blue-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `m-water-yin.webp` — 몽환적 안개

```
Korean man, mid-20s, soft slender build, delicate flowing features, dreamy distant eyes, soft introspective expression, gentle averted gaze, dusty indigo knit, cool misty soft-diffused lighting, upper-body portrait, centered, soft neutral pale-blue-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

---

### 5.2 여성 10장 (사용자가 남성일 때 매칭)

#### `f-wood-yang.webp` — 시원한 봄나무

```
Korean woman, mid-20s, tall slender build, long graceful neck, fresh clean features, high cheekbones, bright confident open expression, direct warm gaze, natural light makeup, moss-green linen blouse, bright crisp natural window light, upper-body portrait, centered, soft neutral beige-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-wood-yin.webp` — 단아한 난초

```
Korean woman, mid-20s, tall slim build, delicate refined features, graceful neck, gentle soft eyes, serene thoughtful expression, subtle side gaze, natural minimal makeup, sage-green silk blouse, soft diffused natural side light, upper-body portrait, centered, soft neutral beige-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-fire-yang.webp` — 빛나는 햇살

```
Korean woman, mid-20s, fit graceful build, defined sparkling eyes, bright radiant smile, vibrant confident energy, engaging direct gaze, warm natural makeup, warm coral knit top, warm golden natural light, upper-body portrait, centered, soft neutral warm-beige gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-fire-yin.webp` — 은은한 노을

```
Korean woman, mid-20s, slim elegant build, expressive warm eyes, soft gentle smile, warmly glowing presence, soft thoughtful gaze, warm subtle makeup, muted rose cashmere sweater, warm soft candle-like lighting, upper-body portrait, centered, soft neutral warm-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-earth-yang.webp` — 따뜻한 대지

```
Korean woman, mid-20s, healthy soft-curved build, round gentle face, warm kind eyes, reassuring warm smile, grounded confident presence, direct warm gaze, natural soft makeup, warm ochre knit cardigan, warm even natural light, upper-body portrait, centered, soft neutral warm-tan gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-earth-yin.webp` — 포근한 흙

```
Korean woman, mid-20s, soft rounded build, gentle round face, kind warm eyes, calm subtle smile, soothing grounded presence, soft gaze, natural minimal makeup, warm beige cotton knit, soft muted natural light, upper-body portrait, centered, soft neutral warm-taupe gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-metal-yang.webp` — 단단한 백자

```
Korean woman, mid-20s, lean defined build, sharp clean features, clear porcelain skin, confident composed eyes, subtle assertive expression, direct poised gaze, crisp minimal makeup, structured ivory wool coat over white blouse, crisp bright lighting, upper-body portrait, centered, soft neutral cool-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-metal-yin.webp` — 차분한 진주

```
Korean woman, mid-20s, slim refined build, delicate angular features, clear pale skin, quiet intelligent eyes, composed soft expression, calm thoughtful gaze, pearly minimal makeup, cream cashmere turtleneck, cool soft diffused lighting, upper-body portrait, centered, soft neutral silver-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-water-yang.webp` — 깊은 호수

```
Korean woman, mid-20s, smooth graceful build, soft defined features, deep expressive dark eyes, mature knowing presence, steady confident gaze, refined natural makeup, navy silk blouse, cool atmospheric lighting with subtle rim light, upper-body portrait, centered, soft neutral deep-blue-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

#### `f-water-yin.webp` — 몽환적 달빛

```
Korean woman, mid-20s, soft slender build, delicate flowing features, dreamy contemplative eyes, serene introspective expression, gentle soft gaze, minimal ethereal makeup, dusty indigo silk blouse, cool misty soft-diffused lighting, upper-body portrait, centered, soft neutral pale-blue-grey gradient background, photorealistic editorial style, subtle film grain, shot on 85mm f/2, --ar 3:4 --style raw --v 6
```

---

## 6. 체크리스트

- [ ] 20장 모두 파일명 규칙 준수 (`{gender}-{element}-{yinyang}.webp`)
- [ ] 3:4 비율, 최소 1024×1365, `.webp` 포맷
- [ ] 배경·조명 방향 20장 전부 동일한 톤
