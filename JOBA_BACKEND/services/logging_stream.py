import logging
import queue
from typing import Optional
from logging.handlers import QueueHandler


# 전역 로그 큐 (모든 모듈에서 공유)
log_queue: "queue.Queue[logging.LogRecord]" = queue.Queue()


def ensure_queue_handler() -> queue.Queue:
    """
    루트 로거에 QueueHandler를 한 번만 추가하여 모든 로그 레코드를 큐에 적재합니다.
    """
    root_logger = logging.getLogger()
    if not any(isinstance(h, QueueHandler) for h in root_logger.handlers):
        root_logger.addHandler(QueueHandler(log_queue))
    if root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)
    return log_queue


def format_record(record: logging.LogRecord) -> str:
    """
    로그 레코드를 단일 행 문자열로 포맷합니다.
    """
    formatter = logging.Formatter("%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    timestamp = formatter.formatTime(record)
    return f"{timestamp} [{record.levelname}] {record.name}: {record.getMessage()}"


