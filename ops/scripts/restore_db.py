#!/usr/bin/env python3
"""
Script de restauration de la base de données Crypto Bot.
Permet de restaurer à partir des différentes méthodes de sauvegarde.
"""

import sys
import os
import subprocess
import json
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import config
from src.logger_settings import logger

Path("logs").mkdir(parents=True, exist_ok=True)
Path("data/backups").mkdir(parents=True, exist_ok=True)


class DatabaseRestore:
    """Classe pour gérer la restauration de la base de données."""

    def __init__(self):
        """Initialise la connexion à la base de données."""
        self.db_url = config.get(
            "database.url", "sqlite:///data/processed/crypto_data.db"
        )
        self.engine = create_engine(self.db_url)
        logger.info(f"🔧 Initialisation du système de restauration - DB: {self.db_url}")

    def list_backups(self):
        """Liste les sauvegardes disponibles."""
        backups = {"sql_dumps": [], "csv_backups": [], "essential_backups": []}

        backup_dir = Path("data/backups")
        if not backup_dir.exists():
            logger.warning("📁 Aucun répertoire de sauvegarde trouvé")
            return backups

        for file in backup_dir.glob("*"):
            if file.is_file():
                if "full_backup" in file.name and file.suffix == ".sql":
                    backups["sql_dumps"].append(file.name)
                elif "essential_backup" in file.name and file.suffix == ".json":
                    backups["essential_backups"].append(file.name)
            elif file.is_dir() and file.name.startswith("csv_"):
                backups["csv_backups"].append(file.name)

        logger.info("📋 Sauvegardes disponibles:")
        for backup_type, files in backups.items():
            logger.info(f"  {backup_type}: {len(files)} sauvegardes")
            for f in files:
                logger.info(f"    - {f}")

        return backups

    def restore_from_sql(self, backup_file):
        """Restaure à partir d'un dump SQL."""
        try:
            backup_path = Path("data/backups") / backup_file
            if not backup_path.exists():
                logger.error(f"❌ Fichier de sauvegarde non trouvé: {backup_file}")
                return False

            logger.info(f"🔄 Restauration SQL en cours depuis: {backup_file}")

            if self.db_url.startswith("sqlite:///"):
                db_path = self.db_url.replace("sqlite:///", "")

                cmd = ["sqlite3", db_path, f".read {backup_path}"]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info(f"✅ Restauration SQL réussie depuis: {backup_file}")
                    return True
                else:
                    logger.error(f"❌ Échec de la restauration SQL: {result.stderr}")
                    return False
            else:
                logger.error("❌ Restauration SQL uniquement supportée pour SQLite")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur lors de la restauration SQL: {e}")
            return False

    def restore_from_csv(self, backup_dir):
        """Restaure à partir d'une sauvegarde CSV."""
        try:
            backup_path = Path("data/backups") / backup_dir
            if not backup_path.exists():
                logger.error(f"❌ Répertoire de sauvegarde non trouvé: {backup_dir}")
                return False

            logger.info(f"🔄 Restauration CSV en cours depuis: {backup_dir}")

            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table'
                """)
                )
                tables = [row[0] for row in result.fetchall()]

            for table_name in ["ohlcv", "ticker"]:
                csv_file = backup_path / f"{table_name}.csv"
                if csv_file.exists():
                    df = pd.read_csv(csv_file)

                    with self.engine.connect() as conn:
                        conn.execute(text(f"DELETE FROM {table_name}"))
                        conn.commit()

                    df.to_sql(table_name, self.engine, if_exists="append", index=False)
                    logger.info(
                        f"✅ Table {table_name} restaurée: {len(df)} enregistrements"
                    )
                else:
                    logger.warning(f"⚠️ Fichier {table_name}.csv non trouvé")

            logger.info(f"✅ Restauration CSV réussie depuis: {backup_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur lors de la restauration CSV: {e}")
            return False

    def restore_from_essential(self, backup_file):
        """Restaure à partir d'une sauvegarde JSON (données essentielles)."""
        try:
            backup_path = Path("data/backups") / backup_file
            if not backup_path.exists():
                logger.error(f"❌ Fichier de sauvegarde non trouvé: {backup_file}")
                return False

            logger.info(
                f"🔄 Restauration des données essentielles depuis: {backup_file}"
            )

            with open(backup_path, "r") as f:
                data = json.load(f)

            logger.info(f"📋 Informations de sauvegarde:")
            logger.info(f"  Date: {data.get('backup_timestamp')}")
            logger.info(f"  Tables: {data.get('tables_info', {}).get('tables', [])}")
            logger.info(
                f"  OHLCV: {data.get('tables_info', {}).get('ohlcv_records', 0)} enregistrements"
            )
            logger.info(
                f"  Ticker: {data.get('tables_info', {}).get('ticker_records', 0)} enregistrements"
            )

            logger.info("ℹ️  La sauvegarde essentielle ne contient que les métadonnées.")
            logger.info(
                "💡 Utilisez une sauvegarde CSV ou SQL pour restaurer les données complètes."
            )

            return True

        except Exception as e:
            logger.error(f"❌ Erreur lors de la restauration JSON: {e}")
            return False

    def verify_restore(self):
        """Vérifie l'intégrité des données après restauration."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                )
                tables = [row[0] for row in result.fetchall()]

            logger.info("🔍 Vérification de la restauration:")
            logger.info(f"  Tables présentes: {tables}")

            for table in tables:
                with self.engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"    {table}: {count} enregistrements")

            return True

        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification: {e}")
            return False

    def interactive_restore(self):
        """Mode interactif pour choisir la sauvegarde à restaurer."""
        backups = self.list_backups()

        if not any(backups.values()):
            logger.error("❌ Aucune sauvegarde disponible")
            return False

        print("\n" + "=" * 50)
        print("MENU DE RESTAURATION")
        print("=" * 50)

        all_backups = []

        if backups["sql_dumps"]:
            print("\n📦 Sauvegardes SQL:")
            for i, f in enumerate(backups["sql_dumps"]):
                print(f"  {len(all_backups)}) {f}")
                all_backups.append(("sql", f))

        if backups["csv_backups"]:
            print("\n📊 Sauvegardes CSV:")
            for i, f in enumerate(backups["csv_backups"]):
                print(f"  {len(all_backups)}) {f}")
                all_backups.append(("csv", f))

        if backups["essential_backups"]:
            print("\n📋 Sauvegardes essentielles (métadonnées):")
            for i, f in enumerate(backups["essential_backups"]):
                print(f"  {len(all_backups)}) {f}")
                all_backups.append(("essential", f))

        print("\n  q) Quitter")
        print("=" * 50)

        choice = input("\n👉 Choisissez une sauvegarde à restaurer: ").strip()

        if choice.lower() == "q":
            print("👋 Annulé")
            return False

        try:
            idx = int(choice)
            if idx < 0 or idx >= len(all_backups):
                print("❌ Choix invalide")
                return False

            backup_type, backup_name = all_backups[idx]

            if backup_type == "sql":
                success = self.restore_from_sql(backup_name)
            elif backup_type == "csv":
                success = self.restore_from_csv(backup_name)
            elif backup_type == "essential":
                success = self.restore_from_essential(backup_name)
            else:
                print("❌ Type de sauvegarde inconnu")
                return False

            if success:
                self.verify_restore()
                print("\n✅ Restauration terminée avec succès!")
            else:
                print("\n❌ Échec de la restauration")

            return success

        except ValueError:
            print("❌ Veuillez entrer un nombre valide")
            return False


if __name__ == "__main__":
    restore = DatabaseRestore()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            restore.list_backups()
        elif sys.argv[1] == "--verify":
            restore.verify_restore()
        else:
            print("Usage: python restore_db.py [--list|--verify]")
    else:
        restore.interactive_restore()
