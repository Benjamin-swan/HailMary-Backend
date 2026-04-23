/**
 * 트랜스포머 단위 테스트.
 * - 순수 함수만 대상이므로 DB/네트워크 의존성 없음.
 * - 확장 정책 이후 기준 (무료 사주 확장 PR): 명리 표준 필드는 노출 허용,
 *   내부 근거 필드(reasoning/score/analysis/gyeokGuk/branchRelations/wolRyeong
 *   /jiJangGan/specialMarks)는 계속 차단.
 */

import { describe, it, expect } from '@jest/globals';
import type { SajuData, Pillar, WuXing } from '../../src/types/index.js';
import { HUE_MAP, hueFor } from '../../src/http/transformers/hueMap.js';
import { toPillarView, unknownHourPillar } from '../../src/http/transformers/pillarView.js';
import { resolveHighlight } from '../../src/http/transformers/sinSalPosition.js';
import { buildFreeSajuResponse } from '../../src/http/transformers/sajuDisplay.js';
import { toWuxingView } from '../../src/http/transformers/wuxingView.js';
import { toYongSinView } from '../../src/http/transformers/yongSinView.js';
import { toDayMasterView } from '../../src/http/transformers/dayMasterView.js';
import { toDaeUnView } from '../../src/http/transformers/daeUnView.js';
import { toTenGodView } from '../../src/http/transformers/tenGodView.js';
import { placeSinSalsByPillar } from '../../src/http/transformers/pillarSinSals.js';
import { getTwelvePhase, TWELVE_PHASE_LABEL } from '../../src/lib/twelve_phases.js';
import type { DaeUnPeriod } from '../../src/lib/dae_un.js';

const pillar = (
  stem: Pillar['stem'],
  branch: Pillar['branch'],
  stemElement: Pillar['stemElement'],
  branchElement: Pillar['branchElement'],
  yinYang: Pillar['yinYang'] = '양'
): Pillar => ({
  stem,
  branch,
  stemElement,
  branchElement,
  yinYang,
});

function makeSaju(overrides: Partial<SajuData> = {}): SajuData {
  return {
    birthDate: '1998-03-15',
    birthTime: '14:30',
    birthCity: '서울',
    calendar: 'solar',
    isLeapMonth: false,
    gender: 'female',
    year: pillar('무', '인', '토', '목', '양'),
    month: pillar('을', '묘', '목', '목', '음'),
    day: pillar('갑', '오', '목', '화', '양'),
    hour: pillar('신', '미', '금', '토', '음'),
    wuxingCount: { 목: 3, 화: 1, 토: 2, 금: 1, 수: 0 },
    tenGods: ['비견', '겁재'],
    tenGodsDistribution: {
      비견: 1,
      겁재: 1,
      식신: 0,
      상관: 0,
      편재: 0,
      정재: 0,
      편관: 0,
      정관: 0,
      편인: 0,
      정인: 0,
    },
    sinSals: ['do_hwa_sal'],
    jiJangGan: {
      year: { primary: { stem: '갑', strength: 100 } },
      month: { primary: { stem: '을', strength: 100 } },
      day: { primary: { stem: '병', strength: 60 }, secondary: { stem: '정', strength: 30 } },
      hour: { primary: { stem: '기', strength: 80 } },
    },
    dayMasterStrength: { level: 'strong', score: 72, analysis: 'test-analysis-secret' },
    gyeokGuk: { gyeokGuk: 'test', name: '정관격', hanja: '正官格', description: 'gyeok-desc' },
    yongSin: { primaryYongSin: '수', secondaryYongSin: '금', reasoning: 'reasoning-secret' },
    branchRelations: { summary: 'relations-secret' },
    wolRyeong: { isDeukRyeong: true, reason: 'wol-secret', strength: 'strong' },
    dominantElements: ['목'],
    weakElements: ['수'],
    specialMarks: ['marker'],
    ...overrides,
  };
}

function makeDaeUnPeriods(): DaeUnPeriod[] {
  return [
    { startAge: 2, endAge: 11, stem: '갑', branch: '오', stemElement: '목', branchElement: '화', pillarIndex: 0 },
    { startAge: 12, endAge: 21, stem: '계', branch: '사', stemElement: '수', branchElement: '화', pillarIndex: 1 },
    { startAge: 22, endAge: 31, stem: '임', branch: '진', stemElement: '수', branchElement: '토', pillarIndex: 2 },
    { startAge: 32, endAge: 41, stem: '신', branch: '묘', stemElement: '금', branchElement: '목', pillarIndex: 3 },
    { startAge: 42, endAge: 51, stem: '경', branch: '인', stemElement: '금', branchElement: '목', pillarIndex: 4 },
    { startAge: 52, endAge: 61, stem: '기', branch: '축', stemElement: '토', branchElement: '토', pillarIndex: 5 },
    { startAge: 62, endAge: 71, stem: '무', branch: '자', stemElement: '토', branchElement: '수', pillarIndex: 6 },
    { startAge: 72, endAge: 81, stem: '정', branch: '해', stemElement: '화', branchElement: '수', pillarIndex: 7 },
  ];
}

describe('hueMap', () => {
  it('maps 오행 to hex', () => {
    expect(HUE_MAP['목']).toBe('#9CC8B0');
    expect(HUE_MAP['화']).toBe('#E6A88E');
    expect(HUE_MAP['토']).toBe('#E6C58E');
    expect(HUE_MAP['금']).toBe('#C5CAD4');
    expect(HUE_MAP['수']).toBe('#6B8BB5');
  });

  it('hueFor 는 천간 오행 기준', () => {
    expect(hueFor('목')).toBe('#9CC8B0');
    expect(hueFor('수')).toBe('#6B8BB5');
  });
});

describe('twelve_phases', () => {
  it('양간 갑 기준: 해=장생, 인=건록, 묘=제왕', () => {
    expect(getTwelvePhase('갑', '해')).toBe('jangsaeng');
    expect(getTwelvePhase('갑', '인')).toBe('geonrok');
    expect(getTwelvePhase('갑', '묘')).toBe('jewang');
  });

  it('음간 을 기준: 오=장생 → 역행', () => {
    expect(getTwelvePhase('을', '오')).toBe('jangsaeng');
    expect(getTwelvePhase('을', '사')).toBe('mokyok');
    expect(getTwelvePhase('을', '묘')).toBe('geonrok');
  });

  it('양간 병 기준: 인=장생, 사=건록', () => {
    expect(getTwelvePhase('병', '인')).toBe('jangsaeng');
    expect(getTwelvePhase('병', '사')).toBe('geonrok');
  });

  it('음간 계 기준: 묘=장생, 자=건록', () => {
    expect(getTwelvePhase('계', '묘')).toBe('jangsaeng');
    expect(getTwelvePhase('계', '자')).toBe('geonrok');
  });

  it('라벨 한자/한글 매핑', () => {
    expect(TWELVE_PHASE_LABEL['jangsaeng']).toEqual({ name: '장생', hanja: '長生' });
    expect(TWELVE_PHASE_LABEL['jewang']).toEqual({ name: '제왕', hanja: '帝旺' });
  });
});

describe('toTenGodView', () => {
  it('일간 갑 기준 천간/지지 십성 계산', () => {
    const view = toTenGodView({
      dayStem: '갑',
      pillarStem: '무',
      pillarBranch: '인',
      branchPrimaryStem: '갑',
    });
    // 갑(양목) vs 무(양토): 편재 (목 극 토, 같은 음양)
    expect(view.heaven).toBe('편재');
    expect(view.heavenHanja).toBe('偏財');
    // 갑 vs 갑(지장간): 비견
    expect(view.earth).toBe('비견');
  });
});

describe('toWuxingView', () => {
  it('counts/ratios/judgments 정확', () => {
    const view = toWuxingView({ 목: 3, 화: 1, 토: 2, 금: 1, 수: 0 });
    expect(view.counts).toEqual({ 목: 3, 화: 1, 토: 2, 금: 1, 수: 0 });
    // 총 7 → 각 비율
    expect(view.ratios['목']).toBeCloseTo(42.9, 1);
    expect(view.ratios['수']).toBe(0);
    expect(view.judgments).toEqual({
      목: '과다',
      화: '적정',
      토: '발달',
      금: '적정',
      수: '결핍',
    });
  });

  it('총합 0 일 때 비율 0', () => {
    const view = toWuxingView({ 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 });
    expect(view.ratios['목']).toBe(0);
    expect(view.judgments['목']).toBe('결핍');
  });
});

describe('toYongSinView', () => {
  it('primary/secondary/opposing(기신=상극) 매핑', () => {
    const saju = makeSaju({
      yongSin: { primaryYongSin: '수', secondaryYongSin: '금', reasoning: 'x' },
    });
    const view = toYongSinView(saju);
    expect(view).not.toBeNull();
    expect(view!.primary).toEqual({ element: '수', hanja: '水', role: '용신' });
    expect(view!.secondary).toEqual({ element: '금', hanja: '金', role: '희신' });
    // 수 극 화
    expect(view!.opposing).toEqual({ element: '화', hanja: '火', role: '기신' });
  });

  it('오행 5순환 기신 검증', () => {
    const cases: Array<[WuXing, WuXing]> = [
      ['목', '토'],
      ['토', '수'],
      ['수', '화'],
      ['화', '금'],
      ['금', '목'],
    ];
    for (const [yong, ki] of cases) {
      const view = toYongSinView(makeSaju({ yongSin: { primaryYongSin: yong, reasoning: 'x' } }));
      expect(view!.opposing.element).toBe(ki);
    }
  });

  it('yongSin 부재 → null', () => {
    const saju = makeSaju();
    delete (saju as Partial<SajuData>).yongSin;
    expect(toYongSinView(saju)).toBeNull();
  });
});

describe('toDayMasterView', () => {
  it('very_weak + score 10 → 극약(1)', () => {
    const v = toDayMasterView(makeSaju({ dayMasterStrength: { level: 'very_weak', score: 10, analysis: '' } }));
    expect(v.strengthLevel).toBe('극약');
    expect(v.strengthPosition).toBe(1);
  });

  it('very_weak + score 20 → 태약(2)', () => {
    const v = toDayMasterView(makeSaju({ dayMasterStrength: { level: 'very_weak', score: 20, analysis: '' } }));
    expect(v.strengthLevel).toBe('태약');
    expect(v.strengthPosition).toBe(2);
  });

  it('weak → 신약(3)', () => {
    const v = toDayMasterView(makeSaju({ dayMasterStrength: { level: 'weak', score: 35, analysis: '' } }));
    expect(v.strengthPosition).toBe(3);
  });

  it('medium → 중화(4)', () => {
    const v = toDayMasterView(makeSaju({ dayMasterStrength: { level: 'medium', score: 50, analysis: '' } }));
    expect(v.strengthPosition).toBe(4);
  });

  it('strong → 신강(5)', () => {
    const v = toDayMasterView(makeSaju({ dayMasterStrength: { level: 'strong', score: 70, analysis: '' } }));
    expect(v.strengthPosition).toBe(5);
  });

  it('very_strong + score 80 → 태강(6)', () => {
    const v = toDayMasterView(
      makeSaju({ dayMasterStrength: { level: 'very_strong', score: 80, analysis: '' } })
    );
    expect(v.strengthPosition).toBe(6);
  });

  it('very_strong + score 95 → 극왕(7)', () => {
    const v = toDayMasterView(
      makeSaju({ dayMasterStrength: { level: 'very_strong', score: 95, analysis: '' } })
    );
    expect(v.strengthPosition).toBe(7);
  });

  it('stem 한자 노출', () => {
    const v = toDayMasterView(makeSaju());
    expect(v.stem).toBe('갑');
    expect(v.stemHanja).toBe('甲');
  });
});

describe('toDaeUnView', () => {
  it('7구간 고정 + 방향 = forward (양남 혹은 음녀)', () => {
    // year.yinYang=양, gender=female → reverse
    const saju = makeSaju();
    const view = toDaeUnView(saju, makeDaeUnPeriods());
    expect(view.periods).toHaveLength(7);
    expect(view.direction).toBe('reverse');
    expect(view.startAge).toBe(2);
  });

  it('양년생 남자 → forward', () => {
    const saju = makeSaju({ gender: 'male' });
    const view = toDaeUnView(saju, makeDaeUnPeriods());
    expect(view.direction).toBe('forward');
  });

  it('startYear = 출생년 + age', () => {
    const saju = makeSaju({ birthDate: '1998-03-15' });
    const view = toDaeUnView(saju, makeDaeUnPeriods());
    expect(view.periods[0]!.startYear).toBe(2000); // 1998 + 2
    expect(view.periods[1]!.startYear).toBe(2010); // 1998 + 12
  });

  it('구간 필드: stem/branch 한자 + element + hue', () => {
    const view = toDaeUnView(makeSaju(), makeDaeUnPeriods());
    const first = view.periods[0]!;
    expect(first.stem).toBe('갑');
    expect(first.stemHanja).toBe('甲');
    expect(first.branchHanja).toBe('午');
    expect(first.element).toBe('목 / 화');
    expect(first.hue).toBe('#9CC8B0');
  });
});

describe('placeSinSalsByPillar', () => {
  it('도화살 위치 배치 (인오술 그룹 → 묘)', () => {
    const saju = makeSaju({
      year: pillar('무', '인', '토', '목', '양'),
      month: pillar('을', '오', '목', '화', '음'),
      day: pillar('갑', '묘', '목', '목', '양'),
      hour: pillar('신', '미', '금', '토', '음'),
      sinSals: ['do_hwa_sal'],
    });
    const result = placeSinSalsByPillar(saju, false);
    expect(result.day.some((e) => e.slug === 'do_hwa_sal')).toBe(true);
    expect(result.year.some((e) => e.slug === 'do_hwa_sal')).toBe(false);
  });

  it('timeUnknown → 시지 제외', () => {
    const saju = makeSaju({
      year: pillar('무', '인', '토', '목', '양'),
      month: pillar('을', '술', '목', '토', '음'),
      day: pillar('갑', '술', '목', '토', '양'),
      hour: pillar('신', '묘', '금', '목', '음'),
      sinSals: ['do_hwa_sal'],
    });
    const excluded = placeSinSalsByPillar(saju, true);
    expect(excluded.hour).toEqual([]);
    const included = placeSinSalsByPillar(saju, false);
    expect(included.hour.some((e) => e.slug === 'do_hwa_sal')).toBe(true);
  });
});

describe('pillarView', () => {
  it('확장 필드(한글/음양/십성/12운성/신살) 포함', () => {
    const view = toPillarView({
      label: '일주',
      pillar: pillar('갑', '자', '목', '수', '양'),
      tenGod: { heaven: '비견', earth: '정인', heavenHanja: '比肩', earthHanja: '正印' },
      twelvePhase: 'mokyok',
      sinSals: [{ slug: 'do_hwa_sal', label: '도화살', hanja: '桃花殺' }],
    });
    expect(view.heaven).toBe('甲');
    expect(view.earth).toBe('子');
    expect(view.heavenHangul).toBe('갑');
    expect(view.earthHangul).toBe('자');
    expect(view.element).toBe('목 / 수');
    expect(view.yinYang).toEqual({ heaven: '양', earth: '양' });
    expect(view.tenGod.heaven).toBe('비견');
    expect(view.twelvePhase).toEqual({ name: '목욕', hanja: '沐浴' });
    expect(view.sinSals).toHaveLength(1);
    expect(view.unknown).toBe(false);
  });

  it('시간 unknown 플레이스홀더', () => {
    const view = unknownHourPillar();
    expect(view.label).toBe('시주');
    expect(view.heaven).toBe('?');
    expect(view.earth).toBe('?');
    expect(view.element).toBe('—');
    expect(view.twelvePhase).toEqual({ name: '—', hanja: '—' });
    expect(view.sinSals).toEqual([]);
    expect(view.unknown).toBe(true);
  });
});

describe('resolveHighlight', () => {
  it('도화살 + 일지 위치', () => {
    const saju = makeSaju({
      day: pillar('갑', '묘', '목', '목'),
      year: pillar('무', '인', '토', '목'),
      sinSals: ['do_hwa_sal'],
    });
    const r = resolveHighlight(saju, false);
    expect(r.text).toBe('도화살(桃花殺) — 日支에 위치');
  });

  it('도화살 부재 시 기본 담백 문구', () => {
    const saju = makeSaju({ sinSals: [] });
    const r = resolveHighlight(saju, false);
    expect(r.text).toBe('명식의 흐름 — 담백한 결');
  });
});

describe('buildFreeSajuResponse', () => {
  it('pillars 항상 길이 4', () => {
    const res = buildFreeSajuResponse({
      saju: makeSaju(),
      daeUnPeriods: makeDaeUnPeriods(),
      sajuRequestId: 'svr_test',
      timeUnknown: false,
    });
    expect(res.pillars).toHaveLength(4);
    expect(res.pillars.map((p) => p.label)).toEqual(['년주', '월주', '일주', '시주']);
  });

  it('time unknown → 시주 플레이스홀더', () => {
    const res = buildFreeSajuResponse({
      saju: makeSaju(),
      daeUnPeriods: makeDaeUnPeriods(),
      sajuRequestId: 'svr_test',
      timeUnknown: true,
    });
    expect(res.pillars[3]!.unknown).toBe(true);
    expect(res.pillars[3]!.heaven).toBe('?');
    expect(res.pillars[2]!.unknown).toBe(false);
  });

  it('최상위 필드 집합: 확장된 계약', () => {
    const res = buildFreeSajuResponse({
      saju: makeSaju(),
      daeUnPeriods: makeDaeUnPeriods(),
      sajuRequestId: 'svr_test',
      timeUnknown: false,
    });
    expect(Object.keys(res).sort()).toEqual(
      ['daeUn', 'dayMaster', 'highlight', 'pillars', 'sajuRequestId', 'wuxing', 'yongSin'].sort()
    );
    expect(res.daeUn.periods).toHaveLength(7);
    expect(res.wuxing.counts).toBeDefined();
    expect(res.dayMaster.strengthScale).toBe(7);
  });

  it('영업 비밀 필드가 응답에 부재 (내부 근거/스코어/원문)', () => {
    const res = buildFreeSajuResponse({
      saju: makeSaju(),
      daeUnPeriods: makeDaeUnPeriods(),
      sajuRequestId: 'svr_test',
      timeUnknown: false,
    });
    const serialized = JSON.stringify(res);
    const forbidden = [
      'wuxingCount',       // 원본 내부 필드명
      'jiJangGan',
      'tenGodsDistribution',
      'dayMasterStrength', // 내부 객체명
      'gyeokGuk',
      'reasoning',         // 용신 근거
      'analysis',          // 신강신약 근거
      'score',             // 신강신약 수치
      'branchRelations',
      'wolRyeong',
      'specialMarks',
      'dominantElements',
      'weakElements',
      'stemElement',
      'branchElement',
      // 비밀 텍스트 원문 중 일부는 fixture 특정 키워드로 역추적
      'reasoning-secret',
      'test-analysis-secret',
      'gyeok-desc',
      'relations-secret',
      'wol-secret',
    ];
    for (const key of forbidden) {
      expect(serialized).not.toContain(key);
    }
  });

  it('sajuRequestId 가 그대로 전달됨', () => {
    const res = buildFreeSajuResponse({
      saju: makeSaju(),
      daeUnPeriods: makeDaeUnPeriods(),
      sajuRequestId: 'svr_ABC123',
      timeUnknown: false,
    });
    expect(res.sajuRequestId).toBe('svr_ABC123');
  });
});
