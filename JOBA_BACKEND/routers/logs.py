from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import queue
from services.logging_stream import ensure_queue_handler, log_queue, format_record


router = APIRouter(prefix="/logs")


@router.get("/stream")
async def stream_logs():
    """
    Server-Sent Events(SSE)로 애플리케이션 로그를 실시간 스트리밍합니다.
    공개 엔드포인트입니다.
    """
    ensure_queue_handler()

    async def event_generator():
        # Non-blocking get, 없으면 짧게 대기하며 폴링
        while True:
            try:
                record = log_queue.get(timeout=1.0)  # type: ignore[arg-type]
                line = format_record(record)
                yield f"data: {line}\n\n"
            except queue.Empty:
                # 하트비트 전송 (옵션)
                yield f": ping\n\n"
                # 짧은 쉬기
                await _sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)


