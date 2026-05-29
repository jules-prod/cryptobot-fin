"""Shared Prometheus metric definitions.

Lives in ``src/`` so both the API image (which copies ``api/`` and ``src/``)
and the collector image (which only copies ``src/``) can import the same
Counter / Histogram instances. ``api/observability.py`` re-exports these.
"""

from __future__ import annotations

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

