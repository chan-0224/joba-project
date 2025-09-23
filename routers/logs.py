from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import queue

from database import get_db, User
from security import decode_token
from services.logging_stream import ensure_queue_handler, log_queue, format_record


router = APIRouter(prefix="/logs")


def require_whitelisted_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> None:
    import os

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = authorization.split()[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    allowed_ids_raw = os.getenv("LOGS_ALLOWED_USER_IDS", "").strip()
    if not allowed_ids_raw:
        raise HTTPException(403, "logs access not configured (empty whitelist)")
    allowed_ids = [s.strip() for s in allowed_ids_raw.split(",") if s.strip()]

    user_id = payload.get("sub")
    if user_id not in allowed_ids:
        raise HTTPException(403, "forbidden")


@router.get("/stream")
async def stream_logs(_auth=Depends(require_whitelisted_user)):
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


