#!/usr/bin/env python3
"""Test des emails *métier* (abonnés) Crypto Bot.

L'alerting opérationnel (santé collecte / erreurs pipeline) est désormais géré
par Prometheus + Grafana (voir infra/README.md). Ce script ne teste plus que
les emails business adressés à un abonné.

Usage:
    python scripts/test_alerts.py --to me@example.com   # envoie les emails business
    python scripts/test_alerts.py --config               # affiche la config sans envoyer
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from src.notifications.notifier import (  # noqa: E402
    _enabled,
    _FROM,
    _HOST,
    _PORT,
    notify_subscribe_confirmation,
    notify_unsubscribe_confirmation,
)

GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def show_config() -> None:
    print(f"\n{BOLD}Configuration emails business{RESET}")
    print(f"  SMTP       : {_HOST}:{_PORT}")
    print(f"  Expéditeur : {_FROM or '(non défini)'}")
    state = GREEN + "OUI" if _enabled() else RED + "NON (FROM ou PASSWORD manquant)"
    print(f"  Actif      : {state}{RESET}\n")


def run_tests(to: str) -> None:
    print(f"\n{BOLD}Test 1 — Confirmation d'inscription{RESET}")
    notify_subscribe_confirmation(
        to,
        articles=[
            {
                "title": "BTC franchit un nouveau seuil",
                "source": "CoinDesk",
                "published_at": "2026-06-09T08:00",
                "sentiment_label": "positive",
            },
        ],
    )
    print(f"  {GREEN}Envoyé (ou ignoré si config manquante){RESET}")

    print(f"\n{BOLD}Test 2 — Confirmation de désabonnement{RESET}")
    notify_unsubscribe_confirmation(to)
    print(f"  {GREEN}Envoyé{RESET}")

    print(f"\n{GREEN}Tests terminés. Vérifiez votre boîte mail.{RESET}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="store_true", help="Affiche la config sans envoyer")
    parser.add_argument("--to", type=str, default="", help="Destinataire de test")
    args = parser.parse_args()

    show_config()
    if args.config:
        sys.exit(0)
    if not _enabled():
        print(f"{RED}Emails désactivés — vérifiez ALERT_EMAIL_FROM et ALERT_EMAIL_PASSWORD{RESET}\n")
        sys.exit(1)
    if not args.to:
        print(f"{RED}Spécifiez un destinataire avec --to me@example.com{RESET}\n")
        sys.exit(1)
    run_tests(args.to)
