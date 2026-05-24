import os
import functools
from flask import Flask

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter \
    import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource


def setup_tracing(app: Flask, service_name: str):
    """
    Configura distributed tracing com OpenTelemetry
    """

    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("APP_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("ENVIRONMENT", "production"),
    })

    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    try:
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, timeout=10))
        )

    except Exception as e:
        print(f"[WARN] OTLP Exporter failed: {e}. Using ConsoleSpanExporter.")
        provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )

    trace.set_tracer_provider(provider)
    FlaskInstrumentor.instrument_app(app)


tracer = trace.get_tracer(__name__)


def traced(span_name: str):
    """
    Decorator to add span to any method

    Usage:
        @traced("debt.create")
        def create_debt(data, session)
            ...
    """
    def decorator(func):
        name = span_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                if "user_id" in kwargs:
                    span.set_attribute("user.id", str(kwargs["user_id"]))

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("status", "success")

                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)

                    raise
        return wrapper
    return decorator
