"""공통 pytest fixtures.

asyncio_mode="auto"는 pyproject.toml에서 설정되어 있어 별도 마커 불필요.
"""
from collections.abc import AsyncGenerator

import fakeredis.aioredis
import pytest

from app.infrastructure.cache.redis_client import RedisCache


@pytest.fixture
async def fake_redis_cache() -> AsyncGenerator[RedisCache, None]:
    """fakeredis 기반 RedisCache. 격리된 in-memory 인스턴스.

    실제 Redis 컨테이너 없이 캐시 hit/miss/TTL 검증 가능.
    """
    cache = RedisCache.__new__(RedisCache)
    cache._redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    try:
        yield cache
    finally:
        await cache._redis.aclose()
