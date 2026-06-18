from datetime import datetime, timedelta
from typing import List
from src.logger_settings import logger


class MarketCache:
    """
    Cache mémoire pour les snapshots globaux CoinGecko.
    Limite de taille pour éviter la surcharge mémoire.
    """

    def __init__(self, max_snapshots: int = 50):
        self.cache: List[dict] = []
        self.max_snapshots = max_snapshots
        logger.info(f"📊 Cache de snapshots initialisé (max {max_snapshots})")

    def add_snapshot(self, snapshot: dict):
        """Ajoute un snapshot avec timestamp"""
        snapshot_entry = {"timestamp": datetime.utcnow(), "data": snapshot}
        self.cache.append(snapshot_entry)

        # Limiter la taille
        if len(self.cache) > self.max_snapshots:
            self.cache.pop(0)

    def get_recent_snapshots(self, minutes: int = 60) -> List[dict]:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [s for s in self.cache if s["timestamp"] >= cutoff]

    def get_latest_snapshot(self) -> dict:
        if not self.cache:
            return {}
        return self.cache[-1]["data"]

    def clear_old_snapshots(self, hours: int = 24):
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        self.cache = [s for s in self.cache if s["timestamp"] >= cutoff]
        logger.info(f"Cache nettoyé: {len(self.cache)} snapshots conservés")
