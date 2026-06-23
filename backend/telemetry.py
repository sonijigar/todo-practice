"""OpenTelemetry metrics setup with Prometheus exporter.

Exposes metrics in Prometheus text format on /metrics.
Import `setup_telemetry(app)` and `ApiMetrics` from main.py to wire everything up.
"""

import time

from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from fastapi import FastAPI, Response


def setup_telemetry(app: FastAPI) -> None:
    """Configure OTel metrics with Prometheus reader and mount /metrics."""

    # ── Resource identifies this service in metrics labels ──
    resource = Resource.create({SERVICE_NAME: "tasks-api"})

    # ── Prometheus reader bridges OTel → prometheus_client REGISTRY ──
    reader = PrometheusMetricReader()

    # ── Set up and register the global MeterProvider ──
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    # ── Expose /metrics endpoint on the FastAPI app ──
    @app.get("/metrics", include_in_schema=False)
    def prometheus_metrics() -> Response:
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST,
        )


class ApiMetrics:
    """Centralised metrics definitions for the tasks API.

    Instruments:
        http_requests_total          – Counter of completed HTTP requests.
        http_request_duration_seconds – Histogram of request latency.

    Usage in an endpoint:
        start = api_metrics.start_timer()
        ...  # business logic
        api_metrics.publish(method="GET", endpoint="/tasks", status=200, start=start)
    """

    def __init__(self) -> None:
        meter = metrics.get_meter("tasks-api")

        self._request_counter = meter.create_counter(
            name="http_requests_total",
            description="Total number of HTTP requests",
            unit="1",
        )

        self._request_duration = meter.create_histogram(
            name="http_request_duration_seconds",
            description="HTTP request latency in seconds",
            unit="s",
        )

    @staticmethod
    def start_timer() -> float:
        """Capture a monotonic timestamp to feed into `publish`."""
        return time.perf_counter()

    def publish(
        self,
        method: str,
        endpoint: str,
        status: int,
        start: float,
    ) -> None:
        """Record one completed request against both instruments."""
        labels = {
            "method": method,
            "endpoint": endpoint,
            "status": str(status),
        }
        self._request_counter.add(1, labels)
        self._request_duration.record(time.perf_counter() - start, labels)


# Module-level singleton — import this in main.py
api_metrics = ApiMetrics()
