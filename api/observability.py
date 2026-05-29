"""
Observability bootstrap for the FastAPI app.

Exposes Prometheus metrics at /metrics, configures OpenTelemetry tracing with
OTLP gRPC export, and wires up structlog JSON logging so the docker loki driver
can ingest structured logs.

All optional dependencies are imported lazily inside ``setup_observability`` so
that the app still boots if the OTel SDK is missing or fails to initialise.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from prometheus_client import Counter, Histogram

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom business metrics — declared once at import time, instrumented from
# the collectors / ETL pipeline modules.
# ---------------------------------------------------------------------------

candles_ingested_total = Counter(
    "candles_ingested_total",
    "Total number of OHLCV candles successfully ingested.",
    labelnames=("symbol", "timeframe", "exchange"),
)

news_collected_total = Counter(
    "news_collected_total",
    "Total number of news articles successfully collected.",
    labelnames=("source",),
)

etl_duration_seconds = Histogram(
    "etl_duration_seconds",
    "Duration of an ETL pipeline run in seconds.",
    labelnames=("pipeline",),
)


_SETUP_DONE = False


def setup_observability(app: "FastAPI") -> None:
    """Wire prometheus, OTel and structlog into ``app``.

    Idempotent: subsequent calls are no-ops. Every optional step is wrapped in
    try/except so that a failure of one subsystem cannot break the app.
    """
    global _SETUP_DONE
    if _SETUP_DONE:
        logger.debug("setup_observability already ran, skipping")
        return

    _setup_structlog()
    _setup_prometheus(app)
    _setup_otel(app)

    _SETUP_DONE = True


def _setup_structlog() -> None:
    """Configure structlog for JSON output on stdout."""
    try:
        import structlog

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("structlog setup failed: %s", exc)


def _setup_prometheus(app: "FastAPI") -> None:
    """Expose /metrics via prometheus-fastapi-instrumentator."""
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=False,
        ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("prometheus instrumentator setup failed: %s", exc)


def _setup_otel(app: "FastAPI") -> None:
    """Initialise OTel tracer + auto-instrument FastAPI/SQLAlchemy/requests/logging."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import (
            ParentBased,
            TraceIdRatioBased,
        )

        service_name = os.environ.get("OTEL_SERVICE_NAME", "cryptobot-api")
        endpoint = os.environ.get(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"
        )
        sampler_arg = float(os.environ.get("OTEL_TRACES_SAMPLER_ARG", "1.0"))

        resource = Resource.create({"service.name": service_name})
        sampler = ParentBased(root=TraceIdRatioBased(sampler_arg))
        provider = TracerProvider(resource=resource, sampler=sampler)
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
        )
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app)

        try:
            from api.dependencies import engine as _engine

            SQLAlchemyInstrumentor().instrument(engine=_engine)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("SQLAlchemy OTel instrumentation failed: %s", exc)

        RequestsInstrumentor().instrument()
        LoggingInstrumentor().instrument(set_logging_format=True)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("OTel setup failed: %s", exc)
