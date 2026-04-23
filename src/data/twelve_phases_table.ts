/**
 * 십이운성(十二運星) 데이터 테이블
 * 일간(천간) × 기준 지지 → 12운성 단계 룩업.
 *
 * 표준 만세력 기준:
 *  - 양간(갑·병·무·경·임): 장생 기준 지지에서 순행(지지 인덱스 +1)
 *  - 음간(을·정·기·신·계): 장생 기준 지지에서 역행(지지 인덱스 -1)
 *
 * 각 일간의 장생(長生) 지지 고정값 (명리서 표준):
 *   갑=해, 을=오, 병=인, 정=유, 무=인, 기=유,
 *   경=사, 신=자, 임=신, 계=묘
 */

import type { HeavenlyStem, EarthlyBranch } from '../types/index.js';

export type TwelvePhase =
  | 'jangsaeng' // 장생 長生
  | 'mokyok' // 목욕 沐浴
  | 'gwandae' // 관대 冠帶
  | 'geonrok' // 건록 建祿
  | 'jewang' // 제왕 帝旺
  | 'soe' // 쇠 衰
  | 'byeong' // 병 病
  | 'sa' // 사 死
  | 'myo' // 묘 墓
  | 'jeol' // 절 絕
  | 'tae' // 태 胎
  | 'yang'; // 양 養

export const TWELVE_PHASE_SEQUENCE: ReadonlyArray<TwelvePhase> = [
  'jangsaeng',
  'mokyok',
  'gwandae',
  'geonrok',
  'jewang',
  'soe',
  'byeong',
  'sa',
  'myo',
  'jeol',
  'tae',
  'yang',
];

export const TWELVE_PHASE_LABEL: Record<TwelvePhase, { name: string; hanja: string }> = {
  jangsaeng: { name: '장생', hanja: '長生' },
  mokyok: { name: '목욕', hanja: '沐浴' },
  gwandae: { name: '관대', hanja: '冠帶' },
  geonrok: { name: '건록', hanja: '建祿' },
  jewang: { name: '제왕', hanja: '帝旺' },
  soe: { name: '쇠', hanja: '衰' },
  byeong: { name: '병', hanja: '病' },
  sa: { name: '사', hanja: '死' },
  myo: { name: '묘', hanja: '墓' },
  jeol: { name: '절', hanja: '絕' },
  tae: { name: '태', hanja: '胎' },
  yang: { name: '양', hanja: '養' },
};

const JANGSAENG_BRANCH: Record<HeavenlyStem, EarthlyBranch> = {
  갑: '해',
  을: '오',
  병: '인',
  정: '유',
  무: '인',
  기: '유',
  경: '사',
  신: '자',
  임: '신',
  계: '묘',
};

const STEM_IS_YANG: Record<HeavenlyStem, boolean> = {
  갑: true,
  을: false,
  병: true,
  정: false,
  무: true,
  기: false,
  경: true,
  신: false,
  임: true,
  계: false,
};

const BRANCH_ORDER: ReadonlyArray<EarthlyBranch> = [
  '자',
  '축',
  '인',
  '묘',
  '진',
  '사',
  '오',
  '미',
  '신',
  '유',
  '술',
  '해',
];

function buildTable(): Record<HeavenlyStem, Record<EarthlyBranch, TwelvePhase>> {
  const stems: HeavenlyStem[] = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
  const result = {} as Record<HeavenlyStem, Record<EarthlyBranch, TwelvePhase>>;

  for (const stem of stems) {
    const startBranch = JANGSAENG_BRANCH[stem];
    const startIndex = BRANCH_ORDER.indexOf(startBranch);
    const direction = STEM_IS_YANG[stem] ? 1 : -1;

    const row = {} as Record<EarthlyBranch, TwelvePhase>;
    for (let step = 0; step < 12; step += 1) {
      const branchIndex = (((startIndex + direction * step) % 12) + 12) % 12;
      const branch = BRANCH_ORDER[branchIndex]!;
      row[branch] = TWELVE_PHASE_SEQUENCE[step]!;
    }
    result[stem] = row;
  }

  return result;
}

export const TWELVE_PHASES_TABLE = buildTable();
