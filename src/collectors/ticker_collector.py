"""
Service de gestion des données de tickers avec stockage hybride :
- cache mémoire pour les données temps réel
- sauvegarde périodique en base de données pour l'historique.
"""

import time
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List
from src.logger_settings import logger
from src.config.settings import config
from src.services.db_context import database_transaction
from src.models.ticker import TickerSnapshot
from src.services.db import get_db_engine
from src.services.exchange_factory import ExchangeFactory
from sqlalchemy import text


class TickerCache:
    """
    Cache mémoire pour les données de tickers en temps réel. limite de taille pour éviter la surcharge mémoire.
    """

    def __init__(self, max_items_per_symbol: int = 100):
        """
        Initialise le cache des tickers.
        """
        self.cache = {}  # format du dict : {symbol: [list of ticker entries]}
        self.max_items = max_items_per_symbol
        logger.info(
            f"📊 Cache de tickers initialisé (max {max_items_per_symbol} par symbole)"
        )

    def add_ticker(self, symbol: str, ticker_data: dict):
        """
        Ajoute un ticker au cache.
        """
        if symbol not in self.cache:
            self.cache[symbol] = []

        # Ajouter le nouveau ticker avec timestamp
        ticker_entry = {"timestamp": datetime.utcnow(), "data": ticker_data}
        self.cache[symbol].append(ticker_entry)

        # Limiter la taille du cache
        if len(self.cache[symbol]) > self.max_items:
            self.cache[symbol].pop(0)  # Supprime le plus ancien

        logger.debug(
            f"✅ Ticker ajouté pour {symbol}: {ticker_data.get('price', ticker_data.get('last', 'N/A'))} USD"
        )

    def get_recent_tickers(self, symbol: str, minutes: int = 60) -> List[dict]:
        """
        Récupère les tickers récents pour un symbole.
        """
        if symbol not in self.cache:
            return []

        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [t for t in self.cache[symbol] if t["timestamp"] >= cutoff]

    def get_current_prices(self) -> Dict[str, dict]:
        """
        Récupère les prix actuels pour tous les symboles.
        """
        return {
            symbol: tickers[-1]["data"]
            for symbol, tickers in self.cache.items()
            if tickers
        }

    def clear_old_data(self, hours: int = 24):
        """
        Nettoie les données plus anciennes que le seuil.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        for symbol in self.cache:
            # Filtrer les tickers récents
            recent = [t for t in self.cache[symbol] if t["timestamp"] >= cutoff]
            self.cache[symbol] = recent

        logger.info(f"Cache nettoyé: conservation des {hours}h précédentes")


class TickerCollector:
    """
    Service de collecte et stockage hybride des données de tickers :
    - cache mémoire pour les données temps réel
    - sauvegarde périodique en base de données pour l'historique.
    """

    def __init__(
        self,
        pairs: List[str],
        exchange: str = "binance",
        snapshot_interval: int = None,
        cache_size: int = None,
        cache_cleanup_interval: int = None,
    ):

        self.pairs = pairs
        self.exchange = exchange.lower()

        # Utiliser la configuration centralisée ou les valeurs par défaut
        self.snapshot_interval = (
            snapshot_interval
            if snapshot_interval is not None
            else config.get("ticker.snapshot_interval", 5)
        )
        self.cache_cleanup_interval = (
            cache_cleanup_interval
            if cache_cleanup_interval is not None
            else config.get("ticker.cache_cleanup_interval", 30)
        )
        cache_size = (
            cache_size
            if cache_size is not None
            else config.get("ticker.cache_size", 100)
        )

        # Initialisation du client d'API en fonction de l'exchange
        self.client = ExchangeFactory.create_exchange(exchange)

        # Initialiser le cache
        self.cache = TickerCache(max_items_per_symbol=cache_size)

        # Thread pour la collecte périodique
        self.collector_thread = None
        self.running = False

        logger.info(f"TickerCollector initialisé pour {exchange} - {len(pairs)} paires")
        logger.info(
            f"   Nettoyage du cache toutes les {self.cache_cleanup_interval} minutes"
        )

    def start_collection(self):
        """
        Démarre la collecte périodique des tickers.
        """
        if self.running:
            logger.warning("⚠️  La collecte est déjà en cours")
            return

        self.running = True
        self.collector_thread = threading.Thread(
            target=self._collection_loop, daemon=True, name="TickerCollector"
        )
        self.collector_thread.start()
        logger.info("Collecte des tickers démarrée")

    def stop_collection(self):
        """
        Arrête la collecte périodique.
        """
        self.running = False
        if self.collector_thread and self.collector_thread.is_alive():
            self.collector_thread.join(timeout=5)
        self.collector_thread = None
        logger.info("Collecte des tickers arrêtée")

    def _collection_loop(self):
        """
        Boucle principale de collecte des tickers.
        """
        next_snapshot = datetime.utcnow() + timedelta(minutes=self.snapshot_interval)

        while self.running:
            try:
                # 1. Récupérer les tickers
                self._fetch_and_cache_tickers()

                # 2. Sauvegarder un snapshot si nécessaire
                if datetime.utcnow() >= next_snapshot:
                    self._save_snapshot()
                    next_snapshot = datetime.utcnow() + timedelta(
                        minutes=self.snapshot_interval
                    )

                # 3. Nettoyer le cache régulièrement
                if datetime.utcnow().minute % self.cache_cleanup_interval == 0:
                    self.cache.clear_old_data(hours=24)

                # Attendre 1 minute
                time.sleep(60)

            except Exception as e:
                logger.error(f"❌ Erreur dans la collecte des tickers: {e}")
                time.sleep(10)  # Attendre avant de réessayer

    def _normalize_ticker_data(self, ticker_data: dict) -> dict:
        """
        Normalise les données de ticker selon l'exchange.
        """
        normalized = ticker_data.copy()

        # Normalisation selon l'exchange
        if self.exchange == "binance":
            # Binance utilise 'last' au lieu de 'price'
            if "last" in normalized and "price" not in normalized:
                normalized["price"] = normalized["last"]

            # Mapping des champs spécifiques à Binance
            if "quoteVolume" in normalized and "volume_24h" not in normalized:
                normalized["volume_24h"] = normalized["quoteVolume"]

            if "percentage" in normalized and "price_change_pct_24h" not in normalized:
                normalized["price_change_pct_24h"] = normalized["percentage"]

        elif self.exchange == "kraken":
            # Kraken a sa propre structure
            if "c" in normalized and "price" not in normalized:
                normalized["price"] = normalized["c"][0]  # Dernier prix

        elif self.exchange == "coinbase":
            # Coinbase utilise 'price' directement
            pass

        return normalized

    def _fetch_and_cache_tickers(self):
        """
        Récupère les tickers depuis l'exchange et les ajoute au cache.
        """
        for pair in self.pairs:
            try:
                ticker = self.client.fetch_ticker(pair)
                if ticker:
                    # Normaliser les données avant de les ajouter au cache
                    normalized_ticker = self._normalize_ticker_data(ticker)
                    self.cache.add_ticker(pair, normalized_ticker)
            except Exception as e:
                logger.error(f"❌ Échec récupération ticker {pair}: {e}")

    def _save_snapshot(self):
        """
        Sauvegarde un snapshot des tickers actuels en base de données.
        Utilise des context managers pour la gestion des ressources.
        """
        try:
            current_prices = self.cache.get_current_prices()

            if not current_prices:
                logger.warning("⚠️  Aucun ticker à sauvegarder")
                return

            # Préparer les snapshots pour la base de données
            snapshots = []
            for symbol, ticker_data in current_prices.items():
                snapshot = TickerSnapshot(
                    id=str(uuid.uuid4()),
                    snapshot_time=datetime.utcnow(),
                    symbol=symbol,
                    exchange=self.exchange,
                    price=ticker_data.get("price"),
                    volume_24h=ticker_data.get("volume_24h"),
                    price_change_24h=ticker_data.get("price_change_24h"),
                    price_change_pct_24h=ticker_data.get("price_change_pct_24h"),
                    high_24h=ticker_data.get("high_24h"),
                    low_24h=ticker_data.get("low_24h"),
                )
                snapshots.append(snapshot)

            # Utiliser un context manager pour la base de données
            with database_transaction() as db_conn:
                for snapshot in snapshots:
                    db_conn.execute(
                        text(
                            """
                            INSERT INTO ticker_snapshots (id, snapshot_time, symbol, exchange, price, volume_24h,
                            price_change_24h, price_change_pct_24h, high_24h, low_24h)
                            VALUES (:id, :snapshot_time, :symbol, :exchange, :price, :volume_24h,
                            :price_change_24h, :price_change_pct_24h, :high_24h, :low_24h)
                            """
                        ),
                        {
                            "id": snapshot.id,
                            "snapshot_time": snapshot.snapshot_time,
                            "symbol": snapshot.symbol,
                            "exchange": snapshot.exchange,
                            "price": snapshot.price,
                            "volume_24h": snapshot.volume_24h,
                            "price_change_24h": snapshot.price_change_24h,
                            "price_change_pct_24h": snapshot.price_change_pct_24h,
                            "high_24h": snapshot.high_24h,
                            "low_24h": snapshot.low_24h,
                        },
                    )

            logger.info(f"Snapshot sauvegardé: {len(snapshots)} tickers")

        except Exception as e:
            logger.error(f"❌ Échec sauvegarde snapshot: {e}")

    def get_current_prices(self) -> Dict[str, dict]:
        """
        Récupère les prix actuels depuis le cache.
        """
        return self.cache.get_current_prices()

    def get_historical_snapshots(self, symbol: str, hours: int = 24) -> List[dict]:
        """
        Récupère l'historique des snapshots depuis la base de données.
        """
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            engine = get_db_engine()

            with engine.connect() as connection:
                from sqlalchemy import text

                result = connection.execute(
                    text(
                        """
                        SELECT * FROM ticker_snapshots
                        WHERE symbol = :symbol AND snapshot_time >= :cutoff
                        ORDER BY snapshot_time DESC
                    """
                    ),
                    {"symbol": symbol, "cutoff": cutoff},
                )
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"❌ Échec récupération historique: {e}")
            return []


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le collecteur
    collector = TickerCollector(
        pairs=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        exchange="binance",
        snapshot_interval=5,  # Sauvegarde toutes les 5 minutes
        cache_size=100,  # 100 tickers max par symbole en cache
    )

    # Démarrer la collecte
    collector.start_collection()

    # Exemple: Récupérer les prix actuels
    try:
        while True:
            time.sleep(10)
            prices = collector.get_current_prices()
            if prices:
                logger.info(f"Prix actuels: {prices}")
    except KeyboardInterrupt:
        collector.stop_collection()
