import argparse
import os
import signal
import time
import subprocess
from logger_settings import logger
from config.settings import config
from src.schedulers.scheduler_ohlcv import OHLCVScheduler
from src.schedulers.scheduler_ticker import TickerScheduler
from src.schedulers.scheduler_market_data import MarketDataScheduler
from src.metrics import record_collection_start, record_collection_success, record_collection_error


def run_collection_once():
    """
    Exécute une collecte unique de données OHLCV et optionnellement de ticker.
    Utilise les nouvelles classes de scheduler.
    """
    ohlcv_scheduler = None
    ticker_scheduler = None
    market_data_scheduler = None

    try:
        logger.info("Démarrage de la collecte unique de données")

        # Récupérer la configuration centralisée
        include_ticker = config.get("ticker.enabled", False)
        include_market_data = config.get("market_data.enabled", True)

        logger.info(
            f"Configuration OHLCV: {len(config.get('pairs'))} paires, {len(config.get('timeframes'))} timeframes"
        )
        logger.info(f"Exchanges: {', '.join(config.get('exchanges'))}")

        if include_ticker:
            logger.info(
                f"Configuration Ticker: {len(config.get('ticker.pairs') or config.get('pairs'))} paires, "
                f"snapshot toutes les {config.get('ticker.snapshot_interval')} minutes"
            )

        if include_market_data:
            logger.info(
                f"Configuration Market Data: Collecte depuis CoinGecko à {config.get('market_data.schedule_time', '10:00')}"
            )

        # 1. Exécuter la collecte OHLCV pour tous les exchanges
        logger.info("📊 Exécution de la collecte OHLCV...")
        ohlcv_scheduler = OHLCVScheduler()
        ohlcv_scheduler.run_once()

        # 2. Démarrer la collecte de ticker si activée
        if include_ticker:
            logger.info("Démarrage de la collecte de ticker en temps réel...")
            ticker_scheduler = TickerScheduler()

            # Exécuter pendant la durée spécifiée
            runtime_minutes = config.get("ticker.runtime", 60)
            if runtime_minutes > 0:
                ticker_scheduler.run_once(runtime_minutes)
            else:
                # Exécution illimitée - démarrer et laisser tourner
                ticker_scheduler.start_collection()
                logger.info("Collecte de ticker en cours (mode illimité)...")

        # 3. Exécuter la collecte Market Data si activée
        if include_market_data:
            logger.info("Exécution de la collecte Market Data (CoinGecko)...")
            market_data_scheduler = MarketDataScheduler()
            market_data_scheduler.run_once()

        logger.info("✅ Collecte OHLCV terminée avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur fatale dans la collecte unique: {e}")
        raise
    finally:
        # Arrêter proprement les schedulers si nécessaire
        if ticker_scheduler and config.get("ticker.runtime", 60) > 0:
            ticker_scheduler.stop_collection()

        # Exécuter le script de vérification de la base de données
        try:
            logger.info("Exécution du script de vérification de la base de données...")
            if os.path.exists("scripts/check_db.py"):
                subprocess.run(["python", "scripts/check_db.py"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Échec de l'exécution du script de vérification: {e}")
        except Exception as e:
            logger.error(
                f"❌ Erreur lors de l'exécution du script de vérification: {e}"
            )


def run_scheduled_collection():
    """
    Exécute une collecte planifiée quotidienne de données OHLCV et optionnellement de ticker.
    Utilise les nouvelles classes de scheduler.
    """
    ohlcv_scheduler = None
    ticker_scheduler = None
    market_data_scheduler = None

    try:
        logger.info("Démarrage du collecteur de données avec planification")

        # Récupérer la configuration centralisée
        include_ticker = config.get("ticker.enabled", False)
        include_market_data = config.get("market_data.enabled", True)

        logger.info(
            f"Configuration OHLCV: {len(config.get('pairs'))} paires, {len(config.get('timeframes'))} timeframes"
        )
        logger.info(
            f"Planification: Collecte quotidienne à {config.get('scheduler.schedule_time', '09:00')}"
        )
        logger.info(f"Exchanges: {', '.join(config.get('exchanges'))}")

        if include_ticker:
            logger.info(
                f"Configuration Ticker: {len(config.get('ticker.pairs') or config.get('pairs'))} paires, "
                f"snapshot toutes les {config.get('ticker.snapshot_interval')} minutes"
            )

        if include_market_data:
            logger.info(
                f"Configuration Market Data: Collecte quotidienne à {config.get('market_data.schedule_time', '10:00')}"
            )

        # 1. Exécution immédiate au démarrage pour chaque exchange
        logger.info("📊 Exécution de la collecte OHLCV initiale...")
        ohlcv_scheduler = OHLCVScheduler()
        ohlcv_scheduler.run_once()

        # 2. Démarrer la collecte de ticker si activée
        if include_ticker:
            logger.info("📈 Démarrage de la collecte de ticker en temps réel...")
            ticker_scheduler = TickerScheduler()
            ticker_scheduler.start_collection()

        # 3. Démarrer la collecte Market Data si activée
        if include_market_data:
            logger.info("Démarrage de la collecte Market Data (CoinGecko)...")
            market_data_scheduler = MarketDataScheduler()
            market_data_scheduler.run_once()  # Exécution immédiate
            market_data_scheduler.start()  # Planification quotidienne

        # 4. Planification quotidienne OHLCV
        logger.info("Démarrage du planificateur quotidien...")
        ohlcv_scheduler.start()

        # Maintenir le processus principal en vie — les schedulers tournent en threads daemon
        # qui seraient tués si le main thread se terminait (et Docker relancerait le container)
        logger.info("✅ Tous les schedulers démarrés — en attente...")
        while True:
            time.sleep(3600)

    except KeyboardInterrupt:
        logger.info("Collecteur arrêté proprement (SIGTERM/CTRL+C)")
    except Exception as e:
        logger.error(f"❌ Erreur fatale dans la collecte planifiée: {e}")
        record_collection_error("planifié")
        raise
    finally:
        # Exécuter le script de vérification de la base de données
        try:
            logger.info("Exécution du script de vérification de la base de données...")
            if os.path.exists("scripts/check_db.py"):
                subprocess.run(["python", "scripts/check_db.py"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Échec de l'exécution du script de vérification: {e}")
        except Exception as e:
            logger.error(
                f"❌ Erreur lors de l'exécution du script de vérification: {e}"
            )


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Collecteur de données marché Crypto Bot"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Activer la planification quotidienne (par défaut: exécution unique)",
    )
    parser.add_argument(
        "--ticker",
        action="store_true",
        help="Activer la collecte de ticker en temps réel",
    )
    parser.add_argument(
        "--ticker-pairs",
        nargs="+",
        default=None,
        help="Liste des paires pour le ticker (par défaut: mêmes que les paires principales)",
    )
    parser.add_argument(
        "--snapshot-interval",
        type=int,
        default=5,
        help="Intervalle de sauvegarde des snapshots de ticker en minutes (par défaut: 5)",
    )
    parser.add_argument(
        "--runtime",
        type=int,
        default=60,
        help="Durée d'exécution en minutes (0 pour illimité, par défaut: 60)",
    )
    parser.add_argument(
        "--exchanges",
        nargs="+",
        default=["binance"],
        help="Liste des exchanges à utiliser (par défaut: binance)",
    )
    parser.add_argument(
        "--schedule-time",
        type=str,
        default="09:00",
        help="Heure de planification quotidienne (format HH:MM, par défaut: 09:00)",
    )
    return parser.parse_args()


def _handle_sigterm(signum, frame):
    raise KeyboardInterrupt()

# SIGTERM (docker compose down) → arrêt propre du collecteur
signal.signal(signal.SIGTERM, _handle_sigterm)


if __name__ == "__main__":
    # Expose prometheus metrics on :8001 (collector container, scraped by prometheus)
    try:
        from prometheus_client import start_http_server

        start_http_server(8001)
        logger.info("📈 Prometheus metrics server started on :8001")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"Failed to start prometheus metrics server: {exc}")

    args = parse_arguments()

    # Mettre à jour la configuration avec les arguments de ligne de commande
    config.update_from_args(args)

    if args.schedule:
        # Mode planifié
        run_scheduled_collection()
    elif args.ticker:
        # Mode ticker seul — métriques Prometheus exposées pour Grafana
        runtime = config.get("ticker.runtime", 60)
        record_collection_start()
        try:
            ticker_scheduler = TickerScheduler()
            ticker_scheduler.run_once(runtime)
            record_collection_success(0)
        except Exception:
            record_collection_error("ticker")
            raise
    else:
        # Mode exécution unique OHLCV
        run_collection_once()
