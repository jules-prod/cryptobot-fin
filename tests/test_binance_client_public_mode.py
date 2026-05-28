"""
Vérifie que BinanceClient peut être instancié sans clés API (mode public-only)
pour les endpoints fetch_ohlcv / fetch_ticker qui n'exigent pas d'auth côté Binance.
"""
import importlib
from unittest.mock import patch


def test_binance_client_constructs_without_keys_in_public_mode():
    """Sans BINANCE_API_KEY ni BINANCE_API_SECRET, le client doit s'initialiser
    en mode public-only (pas d'auth ccxt) et ne PAS lever de ValueError."""
    with patch.dict("os.environ", {}, clear=False):
        import os
        # Vide les vars binance
        for k in ("BINANCE_API_KEY", "BINANCE_API_SECRET"):
            os.environ.pop(k, None)

        # Re-import des settings pour invalider la lecture initiale
        from src.config import settings as cfg_settings
        importlib.reload(cfg_settings)

        # Re-import du client
        from src.services.exchanges_api import binance_client as bc
        importlib.reload(bc)

        # Mock fetch_time + fetch_status pour ne pas faire d'appel réseau
        with patch("ccxt.binance") as mock_binance:
            mock_inst = mock_binance.return_value
            mock_inst.fetch_time.return_value = 0
            mock_inst.milliseconds.return_value = 0
            mock_inst.options = {}
            mock_inst.fetch_status.return_value = {"status": "ok"}

            # Doit construire SANS lever ValueError
            client = bc.BinanceClient()
            assert client is not None

            # ccxt.binance doit être appelé SANS apiKey/secret quand absents
            call_args = mock_binance.call_args[0][0]
            assert "apiKey" not in call_args, f"apiKey should NOT be passed when env empty, got {call_args}"
            assert "secret" not in call_args, f"secret should NOT be passed when env empty, got {call_args}"
