from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import queue

from database import get_db, User
from security import decode_token
from services.logging_stream import ensure_queue_handler, log_queue, format_record


router = APIRouter(prefix="/logs")


def require_admin_or_secret(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_logs_secret: Optional[str] = Header(None, alias="X-Logs-Secret"),
    db: Session = Depends(get_db),
) -> None:
    import os

    logs_secret = os.getenv("LOGS_STREAM_SECRET")
    if logs_secret and x_logs_secret == logs_secret:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = authorization.split()[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    allowed_ids = os.getenv("LOGS_ALLOWED_USER_IDS", "").split(",")
    allowed_ids = [s.strip() for s in allowed_ids if s.strip()]
    user_id = payload.get("sub")
    if allowed_ids and user_id not in allowed_ids:
        raise HTTPException(403, "forbidden")


@router.get("/stream")
async def stream_logs(_auth=Depends(require_admin_or_secret)):
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


