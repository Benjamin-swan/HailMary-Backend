/**
 * Prisma 클라이언트 싱글톤.
 * 핫 리로드 환경(tsx watch)에서 클라이언트 인스턴스가 중복 생성되지 않도록 globalThis 에 캐싱.
 */

import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma: PrismaClient =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'production' ? ['error'] : ['warn', 'error'],
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
