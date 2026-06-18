"""Background scheduler for periodic news RSS collection.

Designed to be started from src.api.main lifespan to keep the news_articles table
populated. Uses lazy imports inside the worker thread so this module itself
has minimal import-time dependencies.
"""

from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)


def start_news_scheduler(interval_minutes: int = 60) -> threading.Thread:
    """Spawn a daemon thread that runs NewsCollector.fetch_and_store every
    interval_minutes minutes.

    interval_minutes <= 0 → single fetch then exit (handy for tests).
    """

    def _run() -> None:
        from src.api.dependencies import SessionLocal
        from src.collectors.news_collector import NewsCollector

        while True:
            try:
                db = SessionLocal()
                try:
                    with NewsCollector() as collector:
                        result = collector.fetch_and_store(db)
                    logger.info("News collector run: %s", result)
                finally:
                    db.close()
            except Exception as exc:  # noqa: BLE001
                logger.warning("News collector run failed: %s", exc)
            if interval_minutes <= 0:
                return
            time.sleep(interval_minutes * 60)

    thread = threading.Thread(target=_run, daemon=True, name="news-scheduler")
    thread.start()
    return thread
