from src.services.exchange_factory import ExchangeFactory
from src.etl.market_data_pipeline.pipeline_market_data import ETLPipelineMarketData
from src.etl.market_data_pipeline.extractor import MarketDataExtractor
from src.etl.market_data_pipeline.transformer import MarketDataTransformer
from src.etl.market_data_pipeline.loader import MarketDataLoader
from src.services.db import get_db_engine
from logger_settings import logger


class MarketDataCollector:
    """
    Collecte les données global_market depuis CoinGecko et les envoie dans le pipeline ETL.
    """

    def __init__(self, rate_limit_delay: float = 2.5):
        self.client = ExchangeFactory.create_exchange(
            "coingecko", rate_limit_delay=rate_limit_delay
        )
        self.pipeline = self._create_pipeline()

    def _create_pipeline(self):
        engine = get_db_engine()
        extractor = MarketDataExtractor(self.client)
        transformer = MarketDataTransformer()
        loader = MarketDataLoader(engine)
        return ETLPipelineMarketData(extractor, transformer, loader)

    def fetch_and_store(self):
        """
        Exécute la collecte des données global_market.
        """
        try:
            logger.info("Lancement pipeline ETL MarketData")
            result = self.pipeline.run("global_market")
            summary = self.pipeline.get_summary({"global_market": result})
            logger.info(f"📊 Résumé: {summary}")
        except Exception as e:
            logger.error(f"❌ Échec collecte pipeline MarketData: {e}")

    def fetch_top_cryptos(self, limit: int = 50, vs_currency: str = "usd"):
        """
        Exécute la collecte des top cryptomonnaies par market cap.

        Args:
            limit: Nombre de cryptos à récupérer (défaut: 50)
            vs_currency: Devise de référence (défaut: "usd")
        """
        try:
            logger.info(f"Collecte top {limit} cryptomonnaies (vs {vs_currency})")

            engine = get_db_engine()
            extractor = MarketDataExtractor(self.client)
            transformer = MarketDataTransformer()
            loader = MarketDataLoader(engine)

            raw_data = extractor.extract_top_cryptos(
                limit=limit, vs_currency=vs_currency
            )
            snapshot, cryptos = transformer.transform_top_cryptos(
                raw_data, vs_currency=vs_currency
            )
            snapshot_id = loader.load_top_cryptos(snapshot, cryptos)

            logger.info(
                f"✅ Top {limit} cryptos collectés et stockés (snapshot_id={snapshot_id})"
            )
            return snapshot_id
        except Exception as e:
            logger.error(f"❌ Échec collecte top cryptos: {e}")
            raise

    def fetch_crypto_details(self, crypto_ids: list):
        """
        Exécute la collecte des détails de cryptomonnaies spécifiques.

        Args:
            crypto_ids: Liste des IDs CoinGecko (ex: ['bitcoin', 'ethereum', 'solana'])
        """
        try:
            logger.info(f"Collecte détails pour {len(crypto_ids)} cryptomonnaies")

            engine = get_db_engine()
            extractor = MarketDataExtractor(self.client)
            transformer = MarketDataTransformer()
            loader = MarketDataLoader(engine)

            raw_data = extractor.extract_crypto_details(crypto_ids)
            if raw_data:
                snapshot, details = transformer.transform_crypto_details(raw_data)
                snapshot_id = loader.load_crypto_details(snapshot, details)
                logger.info(
                    f"✅ Détails de {len(details)} cryptos collectés (snapshot_id={snapshot_id})"
                )
                return snapshot_id
            else:
                logger.warning("⚠️ Aucun détail collecté")
                return None
        except Exception as e:
            logger.error(f"❌ Échec collecte crypto details: {e}")
            raise
