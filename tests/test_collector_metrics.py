"""Tests for the collector health metrics that replaced the operational
SMTP alerts (notify_collect_start/end/error)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from src import metrics
from src.notifications import notifier


def test_record_collection_start_sets_last_run_timestamp() -> None:
    metrics.collector_last_run_timestamp_seconds.set(0)
    metrics.record_collection_start()
    assert metrics.collector_last_run_timestamp_seconds._value.get() > 0


def test_record_collection_success_sets_freshness_and_loaded() -> None:
    metrics.collector_last_success_timestamp_seconds.set(0)
    metrics.record_collection_success(42)
    assert metrics.collector_last_success_timestamp_seconds._value.get() > 0
    assert metrics.collector_last_candles_loaded._value.get() == 42


def test_record_collection_success_clamps_negative_to_zero() -> None:
    metrics.record_collection_success(-5)
    assert metrics.collector_last_candles_loaded._value.get() == 0


def test_record_collection_error_increments_counter_per_trigger() -> None:
    before = metrics.collector_run_errors_total.labels(trigger="planifié")._value.get()
    metrics.record_collection_error("planifié")
    after = metrics.collector_run_errors_total.labels(trigger="planifié")._value.get()
    assert after == before + 1


def test_record_collection_error_default_trigger() -> None:
    metrics.record_collection_error()
    assert metrics.collector_run_errors_total.labels(trigger="unknown")._value.get() >= 1


def test_notifier_business_email_is_noop_without_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    """Business emails must not raise when SMTP is not configured."""
    monkeypatch.setattr(notifier, "_FROM", "")
    monkeypatch.setattr(notifier, "_PWD", "")
    # Should silently no-op, never raise.
    notifier.notify_subscribe_confirmation("user@example.com", articles=[])
    notifier.notify_unsubscribe_confirmation("user@example.com")


def test_notifier_send_skips_empty_recipients() -> None:
    # No recipients → silent no-op regardless of SMTP config.
    notifier._send("subject", "body", recipients=[])
