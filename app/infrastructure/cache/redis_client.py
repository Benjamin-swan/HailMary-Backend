"""Redis 비동기 클라이언트 wrapper (HM-BE-67).

- async get_json/set_json/delete/close
- Redis 다운 시 try/except로 None 반환 → graceful fallback (캐시 미스로 처리)
- BE 503 안 던짐. Redis 장애가 서비스 장애로 번지지 않게.
- 로그는 stderr로 한 줄만 (개인정보 절대 포함 X).
"""
from __future__ import annotations

import contextlib
import json
import logging
from typing import Any

import redis.asyncio as aioredis
from redis.exceptions import RedisError

_log = logging.getLogger(__name__)


class RedisCache:
    """JSON 값 캐시 인터페이스. Domain은 import 금지(infrastructure 전용)."""

    def __init__(self, url: str) -> None:
        # decode_responses=True: bytes → str 자동 변환, json.loads 직접 사용 가능
        self._redis = aioredis.from_url(url, encoding="utf-8", decode_responses=True)

    async def get_json(self, key: str) -> Any | None:
        """캐시 hit 시 디시리얼라이즈된 값 반환, miss/장애 시 None."""
        try:
            raw = await self._redis.get(key)
        except RedisError as exc:
            _log.warning("redis get failed: %s", exc.__class__.__name__)
            return None
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (TypeError, ValueError) as exc:
            _log.warning("redis json decode failed: %s", exc.__class__.__name__)
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """저장 성공 시 True, 장애 시 False (호출자는 결과 무시해도 됨)."""
        try:
            payload = json.dumps(value, ensure_ascii=False)
            await self._redis.set(key, payload, ex=ttl_seconds)
            return True
        except (RedisError, TypeError, ValueError) as exc:
            _log.warning("redis set failed: %s", exc.__class__.__name__)
            return False

    async def delete(self, key: str) -> bool:
        """삭제 성공 시 True, 장애 시 False."""
        try:
            await self._redis.delete(key)
            return True
        except RedisError as exc:
            _log.warning("redis delete failed: %s", exc.__class__.__name__)
            return False

    async def close(self) -> None:
        """앱 종료 시 연결 정리. 실패해도 swallow."""
        with contextlib.suppress(RedisError):
            await self._redis.aclose()
