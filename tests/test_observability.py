"""Tests for the observability bootstrap module (prometheus + OTel + structlog)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.observability import setup_observability


def test_metrics_endpoint_exists() -> None:
    """GET /metrics returns 200 with prometheus text content."""
    app = FastAPI()
    setup_observability(app)
    client = TestClient(app)
    # Generate one request so http_requests_total appears
    client.get("/")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "http_requests_total" in response.text


def test_setup_observability_idempotent() -> None:
    """Calling setup_observability twice on the same app does not raise."""
    app = FastAPI()
    setup_observability(app)
    setup_observability(app)
