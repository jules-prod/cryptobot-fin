"""Emails *métier* (business) à destination des abonnés.

Ce module ne gère QUE les emails business adressés à un abonné précis :
confirmation d'inscription (avec les dernières actualités) et confirmation
de désabonnement.

L'alerting *opérationnel* (santé de la collecte, erreurs de pipeline) a été
migré vers la couche technique Prometheus + Grafana. Les métriques exposées
par le collecteur (``src.metrics.collector_*``) sont scrapées par Prometheus
et les alertes sont routées vers le contact ``cryptobot-email`` de Grafana.
Voir ``infra/README.md`` pour la matrice des alertes.

Configuration via variables d'environnement :
    ALERT_EMAIL_FROM     — expéditeur
    ALERT_EMAIL_PASSWORD — mot de passe app (Gmail : générer dans Sécurité du compte)
    ALERT_SMTP_HOST      — serveur SMTP (défaut : smtp.gmail.com)
    ALERT_SMTP_PORT      — port SMTP    (défaut : 587)

Si ALERT_EMAIL_FROM ou ALERT_EMAIL_PASSWORD est absent, toutes les fonctions
sont des no-ops silencieux.
"""

from __future__ import annotations

import os
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText

from src.logger_settings import logger

_FROM = os.getenv("ALERT_EMAIL_FROM", "").strip()
_PWD = os.getenv("ALERT_EMAIL_PASSWORD", "").strip()
_HOST = os.getenv("ALERT_SMTP_HOST", "smtp.gmail.com")
_PORT = int(os.getenv("ALERT_SMTP_PORT", "587"))


def _enabled() -> bool:
    return bool(_FROM and _PWD)


def _send(subject: str, body: str, recipients: list[str]) -> None:
    """Envoie ``body`` à chaque destinataire explicite. No-op si SMTP non configuré."""
    if not _enabled() or not recipients:
        return
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(_HOST, _PORT) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.login(_FROM, _PWD)
            for to in recipients:
                msg = MIMEText(body, "plain", "utf-8")
                msg["Subject"] = subject
                msg["From"] = _FROM
                msg["To"] = to
                server.sendmail(_FROM, to, msg.as_string())
        logger.info("Email envoyé à %d destinataire(s) : %s", len(recipients), subject)
    except Exception as exc:
        logger.warning("Email non envoyé (non-bloquant) : %s", exc)


def notify_subscribe_confirmation(email: str, articles: list[dict] | None = None) -> None:
    """Envoie un email de confirmation d'inscription avec les dernières actualités."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    news_section = ""
    if articles:
        lines = ["", "─── Dernières actualités ─────────────────────", ""]
        for art in articles[:5]:
            pub = art.get("published_at") or art.get("collected_at") or ""
            if pub:
                pub = str(pub)[:16].replace("T", " ")
            title = art.get("title", "—")
            source = art.get("source", "—")
            url = art.get("url", "")
            label = art.get("sentiment_label", "")
            sentiment_str = f" [{label}]" if label else ""
            lines.append(f"• {title}{sentiment_str}")
            lines.append(f"  {source} · {pub}")
            if url:
                lines.append(f"  {url}")
            lines.append("")
        news_section = "\n".join(lines)

    _send(
        subject="[Crypto Bot] Inscription confirmée aux alertes",
        body=(
            f"Bonjour,\n\n"
            f"Votre inscription aux alertes Crypto Bot a bien été enregistrée.\n\n"
            f"Vous recevrez désormais les actualités et informations Crypto Bot par email.\n\n"
            f"Date d'inscription : {now}\n"
            f"Email : {email}\n"
            f"{news_section}"
            f"\nPour vous désabonner, utilisez le bouton 'Se désabonner' sur la plateforme.\n"
        ),
        recipients=[email],
    )


def notify_unsubscribe_confirmation(email: str) -> None:
    """Envoie un email de confirmation de désabonnement."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    _send(
        subject="[Crypto Bot] Désabonnement confirmé",
        body=(
            f"Bonjour,\n\n"
            f"Votre désabonnement aux alertes Crypto Bot a bien été pris en compte.\n\n"
            f"Date : {now}\n"
            f"Email : {email}\n\n"
            f"Vous ne recevrez plus de notifications.\n"
            f"Vous pouvez vous réinscrire à tout moment depuis la plateforme.\n"
        ),
        recipients=[email],
    )
