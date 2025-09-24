import logging
import queue
from typing import Optional
from logging.handlers import QueueHandler


log_queue: "queue.Queue[logging.LogRecord]" = queue.Queue()


def ensure_queue_handler() -> queue.Queue:
    root_logger = logging.getLogger()
    if not any(isinstance(h, QueueHandler) for h in root_logger.handlers):
        root_logger.addHandler(QueueHandler(log_queue))
    if root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)
    return log_queue


def format_record(record: logging.LogRecord) -> str:
    formatter = logging.Formatter("%Y-%m-%d %H:%M:%S")
    timestamp = formatter.formatTime(record)
    return f"{timestamp} [{record.levelname}] {record.name}: {record.getMessage()}"


