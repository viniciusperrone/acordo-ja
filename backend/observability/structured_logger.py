import logging
import json
from datetime import datetime, timezone

from opentelemetry import trace

from contextvars import ContextVar


_ctx: ContextVar[dict] = ContextVar("log_context", default={})


def get_otel_context():
    span = trace.get_current_span()
    ctx = span.get_span_context()

    if not ctx or not ctx.is_valid:
        return None, None

    trace_id = format(ctx.trace_id, "032x")
    span_id = format(ctx.span_id, "016x")

    return trace_id, span_id


class JSONFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        ctx = _ctx.get()

        trace_id, span_id = get_otel_context()

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": ctx.get("service", "-"),
            "message": record.getMessage(),
            "logger": record.name,
            "trace_id": trace_id or ctx.get("trace_id", "-"),
            "span_id": span_id or ctx.get("span_id", "-"),
            "user_id": ctx.get("user_id", "-"),
            "environment": ctx.get("env", "production"),
            **getattr(record, "extra_fields", {}),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    return logger


def bind_context(**kwargs) -> None:
    current = _ctx.get().copy()
    current.update(kwargs)

    _ctx.set(current)


def clear_context() -> None:
    _ctx.set({})


def log_event(logger, level: str, event: str, exc_info=None, **fields) -> None:
    extra = {"extra_fields": {"event": event, **fields}}

    getattr(logger, level)(event, extra=extra, exc_info=exc_info)
