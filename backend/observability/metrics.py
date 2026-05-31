from flask import Response, Flask
import os

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

from prometheus_client import generate_latest
from prometheus_client import CONTENT_TYPE_LATEST


metric_reader = PrometheusMetricReader()


provider = MeterProvider(
    metric_readers=[metric_reader],
    resource=Resource.create(
        {
            "service.name": "acordoja-api",
            "service.version": os.getenv("APP_VERSION", "1.0.0"),
            "deployment.environment": "production"
        }
    )
)

metrics.set_meter_provider(provider)

meter = metrics.get_meter("acordoja.metrics")

http_requests_total = meter.create_counter(
    name="http_requests_total",
    description="Total HTTP requests",
)

http_request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration in seconds",
    unit="s"
)

external_request_duration = meter.create_histogram(
    name="external_request_duration_seconds",
    description="External request duration in seconds",
    unit="s"
)


class Metrics:

    @staticmethod
    def setup(app: Flask):

        @app.route("/metrics")
        def metrics_endpoint():
            return Response(
                generate_latest(),
                mimetype=CONTENT_TYPE_LATEST,
            )
