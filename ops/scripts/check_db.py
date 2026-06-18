#!/usr/bin/env python3
"""
Script de vérification de la base de données utilisant le DBInspector amélioré.
Alternative moderne au script check_db.py original.
"""

import sys
import os

# Ajouter le dossier racine au path pour les imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.analytics.db_inspector import DBInspector
from src import logger_settings

logger = logger_settings.logger


def main():
    """
    Point d'entrée principal pour la vérification de la base de données. Utiilise la classe DBInspector dans Analytics.
    """
    try:
        logger.info("🔍 Vérification de la base de données avec le DBInspector")

        # Créer l'inspecteur et exécuter la vérification complète
        inspector = DBInspector()

        # Méthode 1: Vérification complète (recommandée)
        inspector.run_complete_check()

    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification: {e}")
        raise


if __name__ == "__main__":
    main()
