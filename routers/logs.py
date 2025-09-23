from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import queue
from services.logging_stream import ensure_queue_handler, log_queue, format_record


router = APIRouter(prefix="/logs")


@router.get("/stream")
async def stream_logs():
    ensure_queue_handler()

    async def event_generator():
        while True:
            try:
                record = log_queue.get(timeout=1.0)  # type: ignore[arg-type]
                line = format_record(record)
                yield f"data: {line}\n\n"
            except queue.Empty:
                yield f": ping\n\n"
                await _sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)


