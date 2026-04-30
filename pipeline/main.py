import sys
import logging
import argparse
from extract import get_client, build_queries, extract
from transform import run as run_transform
from load import run as run_load
from config import (
    BQ_TABLE,
    COUNTRY_CODE_ACTION,
    COUNTRY_CODE_ACTOR,
    YEAR_START,
    BQ_LIMIT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline d'extraction GDELT — Bénin Insights")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les requêtes sans les exécuter (utile pour valider avant BigQuery)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force la réextraction même si les CSV existent déjà (consomme du quota BigQuery)",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="LABEL",
        help="N'exécute que les extractions spécifiées (ex: --only tone_monthly geo_events)",
    )
    return parser.parse_args()


def run(dry_run: bool = False, only: list[str] | None = None, force: bool = False) -> int:
    """
    Orchestre l'extraction complète.

    Returns:
        0 si toutes les extractions réussissent, 1 sinon.
    """
    logger.info("=" * 60)
    logger.info("GDELT Bénin — Pipeline d'extraction")
    logger.info(f"Table    : {BQ_TABLE}")
    logger.info(f"Période  : {YEAR_START} → aujourd'hui")
    logger.info(f"Pays     : action={COUNTRY_CODE_ACTION} | acteur={COUNTRY_CODE_ACTOR}")
    if dry_run:
        logger.info("MODE DRY-RUN activé — aucune requête ne sera envoyée.")
    if force:
        logger.info("MODE FORCE activé — les CSV existants seront réécrasés.")
    logger.info("=" * 60)

    queries = build_queries(
        table=BQ_TABLE,
        action=COUNTRY_CODE_ACTION,
        actor=COUNTRY_CODE_ACTOR,
        year=YEAR_START,
        limit=BQ_LIMIT,
    )

    # Filtrage optionnel par label
    if only:
        unknown = [k for k in only if k not in queries]
        if unknown:
            logger.error(f"Labels inconnus dans --only : {unknown}")
            logger.info(f"Labels disponibles : {list(queries.keys())}")
            return 1
        queries = {k: v for k, v in queries.items() if k in only}
        logger.info(f"Extractions sélectionnées : {list(queries.keys())}")

    # Dry-run : log des requêtes sans exécution
    if dry_run:
        for label, (query, output_path) in queries.items():
            logger.info(f"\n[{label}] → {output_path}\n{query.strip()}\n")
        return 0

    client = get_client()
    results = {"success": [], "failed": []}

    for label, (query, output_path) in queries.items():
        ok = extract(client, query, output_path, label, force=force)
        (results["success"] if ok else results["failed"]).append(label)

    # Rapport final
    total = len(queries)
    nb_ok = len(results["success"])
    nb_ko = len(results["failed"])

    logger.info("=" * 60)
    logger.info(f"Extraction terminée — {nb_ok}/{total} réussies")
    if results["failed"]:
        logger.warning(f"Échecs ({nb_ko}) : {results['failed']}")
    logger.info("=" * 60)

    # Exit code non-zéro si au moins une extraction a échoué
    # Permet à `make extract` de détecter les erreurs
    logger.info("=" * 60)
    logger.info("ÉTAPE 2 — Transformation")
    logger.info("=" * 60)
    transform_exit = run_transform()

    logger.info("=" * 60)
    logger.info("ÉTAPE 3 — Chargement & Export")
    logger.info("=" * 60)
    load_exit = run_load()

    return 0 if (not results["failed"] and transform_exit == 0 and load_exit == 0) else 1


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run(dry_run=args.dry_run, only=args.only, force=args.force))