/**
 * 일간(日干) 뷰 — 신강/신약 7단계 매핑.
 *
 * 내부 `dayMasterStrength.level` 5단계 + `score`(0-100) 를
 * 노출용 7단계 라벨 + position(1~7) 로 재매핑.
 *
 * | 내부 level   | score 범위 | 노출 라벨 | position |
 * | very_weak    | 0-15       | 극약      | 1 |
 * | very_weak    | 16-25      | 태약      | 2 |
 * | weak         | 26-40      | 신약      | 3 |
 * | medium       | 41-60      | 중화      | 4 |
 * | strong       | 61-75      | 신강      | 5 |
 * | very_strong  | 76-90      | 태강      | 6 |
 * | very_strong  | 91-100     | 극왕      | 7 |
 *
 * 영업 비밀: `score` 수치·`analysis` 텍스트는 응답에 포함하지 않는다.
 */

import type { SajuData, HeavenlyStem } from '../../types/index.js';

export type StrengthLevel7 = '극약' | '태약' | '신약' | '중화' | '신강' | '태강' | '극왕';

export interface DayMasterView {
  stem: string;
  stemHanja: string;
  strengthLevel: StrengthLevel7;
  strengthScale: 7;
  strengthPosition: number;
}

const STEM_HANJA: Record<HeavenlyStem, string> = {
  갑: '甲',
  을: '乙',
  병: '丙',
  정: '丁',
  무: '戊',
  기: '己',
  경: '庚',
  신: '辛',
  임: '壬',
  계: '癸',
};

function mapTo7Stage(
  level: NonNullable<SajuData['dayMasterStrength']>['level'],
  score: number
): { label: StrengthLevel7; position: number } {
  const s = Math.max(0, Math.min(100, score));
  switch (level) {
    case 'very_weak':
      return s <= 15 ? { label: '극약', position: 1 } : { label: '태약', position: 2 };
    case 'weak':
      return { label: '신약', position: 3 };
    case 'medium':
      return { label: '중화', position: 4 };
    case 'strong':
      return { label: '신강', position: 5 };
    case 'very_strong':
      return s >= 91 ? { label: '극왕', position: 7 } : { label: '태강', position: 6 };
  }
}

export function toDayMasterView(saju: SajuData): DayMasterView {
  const stem = saju.day.stem;
  const source = saju.dayMasterStrength;
  // 분석 부재 시 안전 폴백: 중화로 처리.
  const level = source?.level ?? 'medium';
  const score = source?.score ?? 50;
  const { label, position } = mapTo7Stage(level, score);
  return {
    stem,
    stemHanja: STEM_HANJA[stem],
    strengthLevel: label,
    strengthScale: 7,
    strengthPosition: position,
  };
}
