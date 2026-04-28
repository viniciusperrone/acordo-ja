import logging
import traceback
import json
from datetime import datetime, timezone

from contextvars import ContextVar


_ctx: ContextVar[dict] = ContextVar("log_context", default={})

class JSONFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        ctx = _ctx.get()
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": ctx.get("service", "-"),
            "message": record.getMessage(),
            "logger": record.name,
            "trace_id": ctx.get("trace_id", "-"),
            "span_id": ctx.get("span_id", "-"),
            "user_id": ctx.get("user_id", "-"),
            "environment": ctx.get("env", "production"),
            **getattr(record, "extra_fields", {}),
        }

        if record.exc_info:
            payload["exception"] = traceback.format_exc()

        return json.dumps(payload, ensure_ascii=False, default=str)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

def bind_context(**kwargs) -> None:
    current = _ctx.get().copy()
    current.update(kwargs)

    _ctx.set(current)

def log_event(logger, level: str, event: str, **fields) -> None:
    extra = {"extra_fields": {"event": event, **fields}}

    getattr(logger, level)(event, extra=extra)
