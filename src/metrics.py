"""Shared Prometheus metric definitions.

Lives in ``src/`` so both the API image (which copies ``api/`` and ``src/``)
and the collector image (which only copies ``src/``) can import the same
Counter / Histogram instances. ``api/observability.py`` re-exports these.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

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
