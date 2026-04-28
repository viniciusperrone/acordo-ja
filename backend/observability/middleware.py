import time
import uuid

from flask import request, g, Flask

from observability.structured_logger import get_logger, bind_context, log_event


class Observability:

    def __init__(self, app: Flask):
        self.init_app(app)

    def init_app(self, app: Flask):
        logger = get_logger("http")

        @app.before_request
        def before_request():
            g.trace_id = request.headers.get("x-trace-id") or str(uuid.uuid4())
            g.start_time = time.perf_counter()

            bind_context(
                trace_id=g.trace_id,
                span_id=str(uuid.uuid4())[:8],
                env="production",
            )

            log_event(
                logger, "info", "http.request.received",
                method=request.method,
                path=request.path,
                client_ip=request.remote_addr,
            )

        @app.after_request
        def after_request(response):
            elapsed_ms = round((time.perf_counter() - g.start_time) * 1000, 2)

            level = "warning" if response.status_code >= 400 else "info"

            log_event(
                logger, level, "http.response.completed",
                status_code=response.status_code,
                duration_ms=elapsed_ms
            )

            response.headers["x-trace-id"] = g.trace_id

            return response

        @app.teardown_request
        def teardown_request(exception):
            if exception:
                log_event(
                    logger, "error", "http.request.failed",
                    error=str(exception),
                )
