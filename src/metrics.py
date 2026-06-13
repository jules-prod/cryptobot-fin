"""Shared Prometheus metric definitions.

Lives in ``src/`` so both the API image (which copies ``api/`` and ``src/``)
and the collector image (which only copies ``src/``) can import the same
Counter / Histogram instances. ``api/observability.py`` re-exports these.
"""

from __future__ import annotations

import time


from prometheus_client import Counter, Gauge, Histogram

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

signals_computed_total = Counter(
    "signals_computed_total",
    "Total number of signals computed.",
    labelnames=("symbol", "signal_type"),
)

paper_trades_total = Counter(
    "paper_trades_total",
    "Total paper trades executed.",
    labelnames=("symbol", "side"),
)

paper_balance_usd = Gauge(
    "paper_balance_usd",
    "Current paper trading balance in USD.",
)

paper_pnl_total = Gauge(
    "paper_pnl_total",
    "Cumulative paper trading PnL in USD.",
)

paper_win_ratio = Gauge(
    "paper_win_ratio",
    "Win ratio of closed paper trades (0-1).",
)


# ---------------------------------------------------------------------------
# Collector / pipeline health
#
# These replace the operational SMTP alerts that previously lived in
# ``src.notifications.notifier`` (notify_collect_start/end/error). The
# technical alerting layer (Prometheus + Grafana) scrapes the collector
# ``/metrics`` endpoint and routes alerts to the ``cryptobot-email`` contact
# point. See ``infra/README.md`` for the alert matrix.
# ---------------------------------------------------------------------------

collector_last_success_timestamp_seconds = Gauge(
    "collector_last_success_timestamp_seconds",
    "Unix timestamp of the last collection run that completed without error.",
)

collector_last_run_timestamp_seconds = Gauge(
    "collector_last_run_timestamp_seconds",
    "Unix timestamp of the most recent collection run attempt.",
)

collector_last_candles_loaded = Gauge(
    "collector_last_candles_loaded",
    "Number of candles inserted by the most recent successful collection run.",
)

collector_run_errors_total = Counter(
    "collector_run_errors_total",
    "Total number of collection runs that ended in an unhandled error.",
    labelnames=("trigger",),
)


def record_collection_start() -> None:
    """Mark the start of a collection run (updates the last-run gauge)."""
    collector_last_run_timestamp_seconds.set(time.time())


def record_collection_success(candles_loaded: int) -> None:
    """Record a successful collection run.

    Updates the freshness gauge (used for the staleness alert) and the count
    of candles loaded by the run (``0`` means data was already up to date).
    """
    collector_last_success_timestamp_seconds.set(time.time())
    collector_last_candles_loaded.set(max(0, candles_loaded))


def record_collection_error(trigger: str = "unknown") -> None:
    """Record a failed collection run for the pipeline-error alert."""
    collector_run_errors_total.labels(trigger=trigger).inc()
