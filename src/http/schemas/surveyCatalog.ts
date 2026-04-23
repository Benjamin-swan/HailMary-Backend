/**
 * 설문 슬러그 카탈로그.
 *
 * DB(`saju_survey.step1/step2`) 에는 슬러그 문자열만 opaque 하게 저장되고,
 * 의미 해석은 이 파일이 유일한 소스다.
 *
 * 용도:
 *   1) PR3 유료 리포트에서 Claude 프롬프트 조립 시 슬러그 → intent 문장으로 확장
 *   2) 백엔드 단독으로도 DB 데이터를 재해석 가능하게 (프론트 레포 부재 대비)
 *   3) 선택적 런타임 검증 — 알 수 없는 슬러그 조기 감지
 *
 * 프론트 단일 소스: `../dohwa_frontend/src/products/dohwaseon/scenes/saju/{doyoon,yeonwoo}/data/surveyOptions.ts`
 * 계약 문서: `../dohwa_frontend/docs/backend-integration.md` §6
 *
 * 설문 변경 정책:
 *   - 라벨 문구만 바뀌면 surveyVersion 유지, 이 파일의 label 만 갱신
 *   - 슬러그가 추가/삭제되거나 step 구조가 바뀌면 새 버전 키(v2 등) 아래에 별도 정의
 *   - 과거 버전 데이터 해석을 위해 구버전 항목은 삭제하지 않고 유지
 */

export interface SurveyOption {
  /** 프론트 화면에 표시되던 한국어 라벨. */
  label: string;
  /** Claude 프롬프트에 주입할 맥락 문장(한 문장). */
  intent: string;
}

export interface SurveyFreeTextSpec {
  type: 'free_text';
  maxLength: number;
  /** 건너뛰기 시 전송 형태: 'null' → `null` 명시 전송, 'omit' → 필드 생략, 'empty' → 빈 문자열. */
  skipPolicy: 'null' | 'omit' | 'empty';
}

export interface SurveyVersionSpec {
  step1: Record<string, SurveyOption>;
  step2: Record<string, SurveyOption>;
  step3: SurveyFreeTextSpec;
}

/**
 * v1 — 최초 공개 버전.
 *
 * 과거 작업 중 한 차례 슬러그 리네이밍이 있었음(프론트 참고):
 *   waiting → waiting_new, dating → crushing(의미 재정의), "missing-ex" → missing_ex
 * 현재 프로덕션에 찍히는 것은 아래 8개가 전부.
 */
const V1: SurveyVersionSpec = {
  step1: {
    waiting_new: {
      label: '새로운 인연을 기다려요',
      intent: '싱글, 적극적으로 새 관계를 찾는 중',
    },
    crushing: {
      label: '썸 타는 중이에요',
      intent: '관계 정의 이전 단계, 일방/쌍방 호감 탐색 중',
    },
    in_relationship: {
      label: '연애 중이에요',
      intent: '교제 중, 현재 관계에 대한 분석 수요',
    },
    missing_ex: {
      label: '헤어진 연인이 그리워요',
      intent: '이별 후, 재결합·미련 영역',
    },
  },
  step2: {
    soulmate: {
      label: '내 운명의 상대',
      intent: '이상적 파트너의 성향/유형',
    },
    timing: {
      label: '다음 인연의 시기',
      intent: '언제 새 인연이 오는지(시간축 질문)',
    },
    compatibility: {
      label: '현재 인연과의 궁합',
      intent: '특정 상대와의 적합성 판정',
    },
    patterns: {
      label: '내 연애 패턴의 본질',
      intent: '반복되는 자기 관계 패턴 진단',
    },
  },
  step3: {
    type: 'free_text',
    maxLength: 100,
    skipPolicy: 'null',
  },
};

export const SURVEY_CATALOG = {
  v1: V1,
} as const;

export type SurveyVersion = keyof typeof SURVEY_CATALOG;

/**
 * 지정 버전의 슬러그가 카탈로그에 존재하는지 확인.
 * 저장은 opaque 하게 허용하지만, 프롬프트 조립 시점에 미등록 슬러그를 조기 발견하려는 용도.
 */
export function isKnownSlug(
  version: SurveyVersion,
  step: 'step1' | 'step2',
  slug: string
): boolean {
  const spec = SURVEY_CATALOG[version];
  return Object.prototype.hasOwnProperty.call(spec[step], slug);
}

/**
 * 슬러그 배열을 "라벨(의도 설명)" 형태 문자열 배열로 확장.
 * 알 수 없는 슬러그는 placeholder 로 유지(로그로 보고하는 책임은 호출자에게).
 */
export function expandSlugs(
  version: SurveyVersion,
  step: 'step1' | 'step2',
  slugs: readonly string[]
): Array<{ slug: string; label: string; intent: string; known: boolean }> {
  const spec = SURVEY_CATALOG[version][step];
  return slugs.map((slug) => {
    const hit = spec[slug];
    if (hit) return { slug, label: hit.label, intent: hit.intent, known: true };
    return { slug, label: slug, intent: '(미등록 슬러그)', known: false };
  });
}
