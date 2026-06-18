"""Tests for src.services.news_scheduler.start_news_scheduler."""
import threading
from unittest.mock import patch, MagicMock


def test_start_news_scheduler_returns_daemon_thread():
    """start_news_scheduler must return a named daemon thread."""
    from src.services.news_scheduler import start_news_scheduler

    with patch("src.collectors.news_collector.NewsCollector") as mock_news_cls:
        mock_inst = mock_news_cls.return_value.__enter__.return_value
        mock_inst.fetch_and_store.return_value = {"new": 0, "duplicate": 0}

        # interval=0 → single fetch then thread exits
        thread = start_news_scheduler(interval_minutes=0)
        assert isinstance(thread, threading.Thread)
        assert thread.daemon is True
        assert thread.name == "news-scheduler"
        thread.join(timeout=3)
        assert not thread.is_alive(), "Thread should have exited with interval=0"
