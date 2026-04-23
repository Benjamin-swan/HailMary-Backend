/**
 * 설문 슬러그 카탈로그 단위 테스트.
 * - v1 에 실제로 프론트가 보내는 슬러그 8개가 등록돼 있는지 회귀 감시.
 * - expandSlugs 확장 출력 검증(알 수 없는 슬러그는 known:false).
 */

import { describe, it, expect } from '@jest/globals';
import {
  SURVEY_CATALOG,
  expandSlugs,
  isKnownSlug,
} from '../../src/http/schemas/surveyCatalog.js';

describe('SURVEY_CATALOG v1', () => {
  it('step1 에 프론트 등록 슬러그 4개가 존재', () => {
    const keys = Object.keys(SURVEY_CATALOG.v1.step1).sort();
    expect(keys).toEqual(['crushing', 'in_relationship', 'missing_ex', 'waiting_new']);
  });

  it('step2 에 프론트 등록 슬러그 4개가 존재', () => {
    const keys = Object.keys(SURVEY_CATALOG.v1.step2).sort();
    expect(keys).toEqual(['compatibility', 'patterns', 'soulmate', 'timing']);
  });

  it('step3 자유 텍스트 스펙은 maxLength 100, skipPolicy null', () => {
    expect(SURVEY_CATALOG.v1.step3).toEqual({
      type: 'free_text',
      maxLength: 100,
      skipPolicy: 'null',
    });
  });

  it('모든 옵션에 label 과 intent 가 비어있지 않다', () => {
    for (const step of ['step1', 'step2'] as const) {
      const spec = SURVEY_CATALOG.v1[step];
      for (const [slug, opt] of Object.entries(spec)) {
        expect(opt.label.length).toBeGreaterThan(0);
        expect(opt.intent.length).toBeGreaterThan(0);
        // intent 는 label 보다 길어야 맥락 설명 역할을 한다.
        expect(opt.intent.length).toBeGreaterThanOrEqual(opt.label.length);
        expect(slug).toMatch(/^[a-z0-9_]+$/);
      }
    }
  });
});

describe('isKnownSlug', () => {
  it('등록 슬러그 → true', () => {
    expect(isKnownSlug('v1', 'step1', 'crushing')).toBe(true);
    expect(isKnownSlug('v1', 'step2', 'soulmate')).toBe(true);
  });

  it('미등록 슬러그 → false', () => {
    expect(isKnownSlug('v1', 'step1', 'ex_lover')).toBe(false); // 과거 오염 값
    expect(isKnownSlug('v1', 'step2', 'pattern')).toBe(false); // 단수형 오타
  });

  it('prototype 오염 방지 — __proto__, hasOwnProperty 같은 키는 false', () => {
    expect(isKnownSlug('v1', 'step1', '__proto__')).toBe(false);
    expect(isKnownSlug('v1', 'step1', 'hasOwnProperty')).toBe(false);
  });
});

describe('expandSlugs', () => {
  it('등록 슬러그 배열 → label + intent 로 확장', () => {
    const out = expandSlugs('v1', 'step2', ['soulmate', 'compatibility']);
    expect(out).toEqual([
      {
        slug: 'soulmate',
        label: '내 운명의 상대',
        intent: '이상적 파트너의 성향/유형',
        known: true,
      },
      {
        slug: 'compatibility',
        label: '현재 인연과의 궁합',
        intent: '특정 상대와의 적합성 판정',
        known: true,
      },
    ]);
  });

  it('미등록 슬러그 → known:false, 라벨은 슬러그 그대로', () => {
    const out = expandSlugs('v1', 'step1', ['crushing', 'ex_lover']);
    expect(out[0]!.known).toBe(true);
    expect(out[1]).toEqual({
      slug: 'ex_lover',
      label: 'ex_lover',
      intent: '(미등록 슬러그)',
      known: false,
    });
  });

  it('빈 배열 → 빈 배열', () => {
    expect(expandSlugs('v1', 'step1', [])).toEqual([]);
  });
});
