import logging
import queue
from typing import Optional
from logging.handlers import QueueHandler
import os

# Optional Redis imports (graceful fallback when redis is unavailable)
try:
    import redis  # sync client for logging handler publish
except Exception:  # pragma: no cover
    redis = None  # type: ignore

try:
    import redis.asyncio as aioredis  # async client for SSE subscriber
except Exception:  # pragma: no cover
    aioredis = None  # type: ignore

REDIS_URL: Optional[str] = os.getenv("REDIS_URL")


log_queue: "queue.Queue[logging.LogRecord]" = queue.Queue()


def ensure_queue_handler() -> queue.Queue:
    root_logger = logging.getLogger()
    if not any(isinstance(h, QueueHandler) for h in root_logger.handlers):
        root_logger.addHandler(QueueHandler(log_queue))
    if root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)
    return log_queue


class RedisLogHandler(logging.Handler):
    """
    Logging handler that publishes formatted records to a Redis Pub/Sub channel.
    """

    def __init__(self, channel: str = "app_logs"):
        super().__init__()
        self.channel = channel
        self._client = None
        if redis and REDIS_URL:
            try:
                self._client = redis.from_url(REDIS_URL, decode_responses=True)
            except Exception:
                self._client = None

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        if not self._client:
            return
        try:
            line = format_record(record)
            # Publish as plain text line; subscriber will wrap as SSE
            self._client.publish(self.channel, line)
        except Exception:
            # Do not raise from logging handler
            pass


def ensure_redis_handler(channel: str = "app_logs") -> bool:
    """
    Attach RedisLogHandler to root logger if REDIS_URL and redis are available.
    Returns True when attached/available, False otherwise.
    """
    if not (REDIS_URL and redis):
        return False

    root_logger = logging.getLogger()
    if not any(isinstance(h, RedisLogHandler) for h in root_logger.handlers):
        try:
            root_logger.addHandler(RedisLogHandler(channel=channel))
        except Exception:
            return False
    if root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)
    return True


def format_record(record: logging.LogRecord) -> str:
    formatter = logging.Formatter("%Y-%m-%d %H:%M:%S")
    timestamp = formatter.formatTime(record)
    return f"{timestamp} [{record.levelname}] {record.name}: {record.getMessage()}"


async def sse_event_stream(channel: str = "app_logs"):
    """
    Async generator that yields SSE-formatted lines from either:
    - Redis Pub/Sub (when REDIS_URL and redis are available), or
    - In-process queue fallback (single-worker scenarios)

    It also emits periodic comment pings to keep the connection alive.
    """
    # Prefer Redis when available
    if REDIS_URL and aioredis:
        import asyncio
        client = aioredis.from_url(REDIS_URL, decode_responses=True)
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        try:
            while True:
                try:
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message and message.get("type") == "message":
                        data = message.get("data")
                        if data:
                            yield f"data: {data}\n\n"
                            continue
                    # idle -> ping
                    yield f": ping\n\n"
                    await asyncio.sleep(0.5)
                except Exception:
                    # On any error, small backoff + ping to keep stream alive
                    yield f": ping\n\n"
                    await asyncio.sleep(0.5)
        finally:
            try:
                await pubsub.unsubscribe(channel)
            except Exception:
                pass
            try:
                await pubsub.close()
            except Exception:
                pass
            try:
                await client.close()
            except Exception:
                pass

    # Fallback: In-process queue (single worker)
    import asyncio
    ensure_queue_handler()
    while True:
        try:
            record = log_queue.get(timeout=1.0)  # type: ignore[arg-type]
            line = format_record(record)
            yield f"data: {line}\n\n"
        except queue.Empty:
            # heartbeat
            yield f": ping\n\n"
            await asyncio.sleep(0.5)

