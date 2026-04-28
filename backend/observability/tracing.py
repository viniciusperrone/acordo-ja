from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter \
    import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
import functools

from flask import Flask


def setup_tracing(app: Flask, service_name: str):
    resource = Resource.create({
        "service_name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": "production",
    })

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(
            endpoint="http://otel-collector:4317"
        ))
    )

    trace.set_tracer_provider(provider)
    FlaskInstrumentor.instrument_app(app)

tracer = trace.get_tracer("")

def traced(span_name: str):
    """Decorator to add span to any method"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute({
                    "user_id": kwargs.get("user_id", "-"),
                })

                return await func(*args, **kwargs)
        return wrapper
    return decorator

# Use in services
# @traced("debt.generate_proposals")
# async def generate_proposals(debt_id, user_id, amount): ...
