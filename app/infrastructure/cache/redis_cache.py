"""Redis Cache Service Implementation.

Production-ready implementation dengan:
- Connection Pool eksplisit
- Retry mechanism dengan ExponentialBackoff
- Health check
- Proper error handling dengan graceful degradation
- Logging untuk monitoring
"""

import json
import logging
import time
from typing import Any

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.config import get_settings
from app.domain.entities.chat_message import ChatMessage
from app.domain.interfaces.cache_service import ICacheService

logger = logging.getLogger(__name__)


class RedisCacheService(ICacheService):
    """Redis Cache Service dengan production-ready features."""

    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        self._client = redis_client
        self._pool: ConnectionPool | None = None
        self._settings = get_settings()
        self._is_connected = False

    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client dengan connection pool dan retry mechanism."""
        if self._client is None:
            try:
                # Connection Pool dengan konfigurasi eksplisit
                self._pool = ConnectionPool.from_url(
                    self._settings.redis_url,
                    max_connections=self._settings.redis_max_connections,
                    socket_timeout=float(self._settings.redis_socket_timeout),
                    socket_connect_timeout=float(self._settings.redis_connect_timeout),
                    health_check_interval=self._settings.redis_health_check_interval,
                    decode_responses=True,
                    encoding="utf-8",
                )

                # Retry mechanism dengan ExponentialBackoff
                retry = Retry(
                    ExponentialBackoff(),
                    retries=self._settings.redis_retry_attempts,
                )

                self._client = redis.Redis(
                    connection_pool=self._pool,
                    retry=retry,
                    retry_on_error=[ConnectionError, TimeoutError, RedisError],
                )

                # Test connection
                await self._client.ping()
                self._is_connected = True
                logger.info("Redis connection established successfully")

            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._is_connected = False
                raise

        return self._client

    async def close(self) -> None:
        """Close Redis connection dan cleanup resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            self._is_connected = False
            logger.info("Redis connection closed")

        if self._pool is not None:
            await self._pool.disconnect()
            self._pool = None

    async def health_check(self) -> dict[str, Any]:
        """Check Redis connectivity dan return health status."""
        result = {
            "status": "unhealthy",
            "connected": False,
            "latency_ms": None,
            "error": None,
        }

        try:
            client = await self._get_client()
            start_time = time.time()
            await client.ping()
            latency = (time.time() - start_time) * 1000

            result.update({
                "status": "healthy",
                "connected": True,
                "latency_ms": round(latency, 2),
            })

        except (ConnectionError, TimeoutError, RedisError) as e:
            result["error"] = str(e)
            logger.warning(f"Redis health check failed: {e}")

        return result

    async def get(self, key: str) -> Any | None:
        """Get value dari cache dengan graceful degradation."""
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis GET failed for key '{key}': {e}")
            return None  # Graceful degradation
        except RedisError as e:
            logger.error(f"Redis error on GET for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value ke cache dengan graceful degradation."""
        try:
            client = await self._get_client()
            if ttl is None:
                ttl = self._settings.cache_ttl

            serialized = json.dumps(value) if not isinstance(value, str) else value
            await client.setex(key, ttl, serialized)
            return True

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis SET failed for key '{key}': {e}")
            return False  # Graceful degradation
        except RedisError as e:
            logger.error(f"Redis error on SET for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key dari cache dengan graceful degradation."""
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return result > 0

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis DELETE failed for key '{key}': {e}")
            return False
        except RedisError as e:
            logger.error(f"Redis error on DELETE for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists dengan graceful degradation."""
        try:
            client = await self._get_client()
            return await client.exists(key) > 0

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis EXISTS failed for key '{key}': {e}")
            return False
        except RedisError as e:
            logger.error(f"Redis error on EXISTS for key '{key}': {e}")
            return False

    def _chat_history_key(self, session_id: str) -> str:
        """Generate key untuk chat history."""
        return f"chat:history:{session_id}"

    async def get_chat_history(
        self, session_id: str, limit: int = 20
    ) -> list[ChatMessage]:
        """Get chat history dengan graceful degradation."""
        try:
            client = await self._get_client()
            key = self._chat_history_key(session_id)
            messages_json = await client.lrange(key, -limit, -1)

            messages = []
            for msg_json in messages_json:
                try:
                    data = json.loads(msg_json)
                    messages.append(ChatMessage(**data))
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse chat message: {e}")
                    continue

            return messages

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis GET_CHAT_HISTORY failed for session '{session_id}': {e}")
            return []  # Graceful degradation
        except RedisError as e:
            logger.error(f"Redis error on GET_CHAT_HISTORY for session '{session_id}': {e}")
            return []

    async def save_chat_message(self, session_id: str, message: ChatMessage) -> bool:
        """Save chat message dengan graceful degradation."""
        try:
            client = await self._get_client()
            key = self._chat_history_key(session_id)

            msg_data = {
                "id": str(message.id),
                "session_id": message.session_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }

            await client.rpush(key, json.dumps(msg_data))
            await client.expire(key, self._settings.chat_history_ttl)
            return True

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis SAVE_CHAT_MESSAGE failed for session '{session_id}': {e}")
            return False
        except RedisError as e:
            logger.error(f"Redis error on SAVE_CHAT_MESSAGE for session '{session_id}': {e}")
            return False

    async def clear_chat_history(self, session_id: str) -> bool:
        """Clear chat history dengan graceful degradation."""
        try:
            client = await self._get_client()
            key = self._chat_history_key(session_id)
            result = await client.delete(key)
            return result > 0

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis CLEAR_CHAT_HISTORY failed for session '{session_id}': {e}")
            return False
        except RedisError as e:
            logger.error(f"Redis error on CLEAR_CHAT_HISTORY for session '{session_id}': {e}")
            return False
