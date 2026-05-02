import os
import logging
from pathlib import Path
from google.cloud import bigquery
import pandas as pd
from config import (
    USE_BIGQUERY,
    DATA_RAW_PATH,
    DATA_RAW_GEO_PATH,
)

# CONFIGURATION DU LOGGER
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# INITIALISATION BIGQUERY
def get_client() -> bigquery.Client:
    """Initialise et retourne le client BigQuery."""
    if not USE_BIGQUERY:
        logger.warning("Mode local activé — BigQuery désactivé.")
        return None

    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        bq_client = bigquery.Client(project=project)
        logger.info("Connexion BigQuery établie.")
        return bq_client
    except Exception as e:
        logger.error(f"Erreur connexion BigQuery : {e}")
        return None


# FONCTION D'EXTRACTION GÉNÉRIQUE
def extract(client: bigquery.Client, query: str, output_path: str, label: str, force: bool = False) -> bool:
    """
    Exécute une requête BigQuery et sauvegarde le résultat en CSV.
    Si le fichier CSV existe déjà, la requête est skippée (protection quota).

    Args:
        client      : client BigQuery initialisé
        query       : requête SQL à exécuter
        output_path : chemin de sortie du fichier CSV
        label       : nom lisible pour les logs
        force       : si True, réextrait même si le fichier existe déjà

    Returns:
        True si succès ou fichier déjà présent, False si erreur
    """
    
    # MODE LOCAL — extraction ignorée
    if client is None:
        logger.warning(f"{label} : mode local → extraction ignorée.")
        return True
        
    # CACHE CHECK — skip si fichier déjà présent
    if not force and Path(output_path).exists():
        size_kb = Path(output_path).stat().st_size // 1024
        logger.info(f"[CACHE] {label} : fichier existant ({size_kb} KB) → BigQuery skippé.")
        return True

    try:
        logger.info(f"Extraction : {label}...")
        df = client.query(query).to_dataframe()

        if df.empty:
            logger.warning(f"{label} : aucun résultat retourné.")
            return False

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"{label} : {len(df)} lignes → {output_path}")
        return True

    except Exception as e:
        logger.error(f"{label} : erreur lors de l'extraction — {e}")
        return False


# DÉFINITION DES REQUÊTES
def build_queries(table: str, action: str, actor: str, year: int, limit: int) -> dict:
    """
    Construit toutes les requêtes SQL à partir des paramètres config.

    Returns:
        dict : {label -> (query, output_path)}
    """
    cols = ", ".join([
        "SQLDATE", "Actor1Name", "Actor1CountryCode",
        "Actor2Name", "Actor2CountryCode",
        "EventCode", "EventBaseCode", "EventRootCode",
        "GoldsteinScale", "NumArticles", "AvgTone",
        "ActionGeo_FullName", "ActionGeo_CountryCode",
        "ActionGeo_Lat", "ActionGeo_Long", "SOURCEURL"
    ])

    base_filter = f"""
        WHERE ActionGeo_CountryCode = '{action}'
          AND YEAR >= {year}
    """

    return {

        # DONNÉES DE BASE
        "gdelt_benin_main": (
            f"SELECT {cols} FROM `{table}` {base_filter} LIMIT {limit}",
            DATA_RAW_PATH
        ),


        "geo_events": (
            f"""
            SELECT
              SQLDATE, Actor1Name, Actor2Name, EventRootCode,
              GoldsteinScale, AvgTone, NumArticles,
              ActionGeo_FullName, ActionGeo_Lat, ActionGeo_Long, SOURCEURL
            FROM `{table}` {base_filter}
              AND ActionGeo_Lat IS NOT NULL
              AND ActionGeo_Long IS NOT NULL
              AND ActionGeo_Lat != 9.5
              AND ActionGeo_Long != 2.25
            LIMIT 5000
            """,
            DATA_RAW_GEO_PATH
        ),

    }