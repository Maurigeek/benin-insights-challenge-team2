import json
import logging
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import (
    DATA_CLEAN_PATH,
    DATA_TONE_PATH,
    DATA_ACTORS_PATH,
    DATA_EVENTS_PATH,
    DATA_GEO_PATH,
    DATA_ZOOM_DEC2025_PATH,
    DATA_ZOOM_ELECTION_PATH,
    DATA_CULTURE_PATH,
    DATA_COOPERATION_NGA_PATH,
    DATA_SECURITE_NORD_PATH,
    DATA_FEMMES_PATH,
    DATA_CHINE_PATH,
    DATA_PERSO_BENIN_PATH,
    DATA_PERSO_ETRANGERES_PATH,
    DATA_LIBERTE_PRESSE_PATH,
    DATA_CAN2025_PATH,
    DATA_ECONOMIE_PATH,
    DATA_SOURCES_OFF_PATH,
    DATA_MEDIAS_BENINOIS_PATH,
    DATA_MEDIAS_INTERNATIONAUX_PATH,
)

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------

# Seuil à partir duquel on génère un Parquet (en lignes)
PARQUET_MIN_ROWS = 500

# Bounding box Bénin (WGS84)
BENIN_BBOX = {"lat_min": 6.0, "lat_max": 12.5, "lon_min": 0.7, "lon_max": 3.9}

# Dossiers de sortie
DIR_CSV     = Path("data/processed")
DIR_PARQUET = Path("data/processed/parquet")
DIR_GEOJSON = Path("data/processed/geojson")
DIR_REPORTS = Path("reports")

# ---------------------------------------------------------------------------
# SCHÉMAS DE VALIDATION PAR DATASET
# Format : label → {colonnes_requises, colonnes_critiques_non_null, a_geo}
# ---------------------------------------------------------------------------
SCHEMAS: dict[str, dict] = {
    "gdelt_benin_clean": {
        "required_cols":  ["date", "Actor1Name", "EventRootCode", "AvgTone", "GoldsteinScale", "SOURCEURL"],
        "non_null_cols":  ["date", "EventRootCode", "AvgTone"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "tone_monthly": {
        "required_cols":  ["date", "ton_moyen", "nb_evenements"],
        "non_null_cols":  ["date", "ton_moyen"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "actors_country": {
        "required_cols":  ["Actor2CountryCode", "nb_interactions"],
        "non_null_cols":  ["Actor2CountryCode", "nb_interactions"],
        "has_geo":        False,
        "date_col":       None,
    },
    "events_by_type": {
        "required_cols":  ["EventRootCode", "nb_evenements", "stabilite_moyenne", "ton_moyen"],
        "non_null_cols":  ["EventRootCode", "nb_evenements"],
        "has_geo":        False,
        "date_col":       None,
    },
    "geo_events": {
        "required_cols":  ["date", "EventRootCode", "ActionGeo_Lat", "ActionGeo_Long", "AvgTone"],
        "non_null_cols":  ["date", "ActionGeo_Lat", "ActionGeo_Long"],
        "has_geo":        True,
        "date_col":       "date",
    },
    "zoom_dec2025": {
        "required_cols":  ["date", "Actor1Name", "EventRootCode", "AvgTone"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "zoom_election2026": {
        "required_cols":  ["date", "Actor1Name", "EventRootCode", "AvgTone"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "culture_tourisme": {
        "required_cols":  ["date", "EventRootCode", "AvgTone", "ActionGeo_FullName"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        True,
        "date_col":       "date",
    },
    "cooperation_ben_nga": {
        "required_cols":  ["date", "Actor1CountryCode", "Actor2CountryCode", "EventRootCode", "AvgTone"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "securite_nord": {
        "required_cols":  ["date", "EventRootCode", "GoldsteinScale", "ActionGeo_Lat", "ActionGeo_Long"],
        "non_null_cols":  ["date", "EventRootCode", "ActionGeo_Lat", "ActionGeo_Long"],
        "has_geo":        True,
        "date_col":       "date",
    },
    "femmes_benin": {
        "required_cols":  ["date", "EventRootCode", "AvgTone", "ActionGeo_FullName"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "chine_benin": {
        "required_cols":  ["date", "Actor1CountryCode", "Actor2CountryCode", "EventRootCode", "AvgTone"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "personnalites_benin": {
        "required_cols":  ["date", "Actor1Name", "EventRootCode", "AvgTone"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "personnalites_etrangeres": {
        "required_cols":  ["date", "Actor1Name", "EventRootCode", "AvgTone"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "liberte_presse": {
        "required_cols":  ["date", "EventRootCode", "AvgTone", "GoldsteinScale"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "can2025_sport": {
        "required_cols":  ["date", "Actor1Name", "EventRootCode", "AvgTone"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "economie": {
        "required_cols":  ["date", "EventRootCode", "AvgTone", "SOURCEURL"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "sources_officielles": {
        "required_cols":  ["date", "EventRootCode", "AvgTone", "SOURCEURL"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "medias_beninois": {
        "required_cols":  ["date", "EventRootCode", "AvgTone", "SOURCEURL"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
    "medias_internationaux": {
        "required_cols":  ["date", "EventRootCode", "AvgTone", "SOURCEURL"],
        "non_null_cols":  ["date", "EventRootCode"],
        "has_geo":        False,
        "date_col":       "date",
    },
}

# ---------------------------------------------------------------------------
# REGISTRE DES FICHIERS
# Format : label → input_path (sortie de transform.py)
# ---------------------------------------------------------------------------
REGISTRY: dict[str, str] = {
    "gdelt_benin_clean":       DATA_CLEAN_PATH,
    "tone_monthly":            DATA_TONE_PATH,
    "actors_country":          DATA_ACTORS_PATH,
    "events_by_type":          DATA_EVENTS_PATH,
    "geo_events":              DATA_GEO_PATH,
    "zoom_dec2025":            DATA_ZOOM_DEC2025_PATH,
    "zoom_election2026":       DATA_ZOOM_ELECTION_PATH,
    "culture_tourisme":        DATA_CULTURE_PATH,
    "cooperation_ben_nga":     DATA_COOPERATION_NGA_PATH,
    "securite_nord":           DATA_SECURITE_NORD_PATH,
    "femmes_benin":            DATA_FEMMES_PATH,
    "chine_benin":             DATA_CHINE_PATH,
    "personnalites_benin":     DATA_PERSO_BENIN_PATH,
    "personnalites_etrangeres":DATA_PERSO_ETRANGERES_PATH,
    "liberte_presse":          DATA_LIBERTE_PRESSE_PATH,
    "can2025_sport":      DATA_CAN2025_PATH,
    "economie":           DATA_ECONOMIE_PATH,
    "sources_officielles":DATA_SOURCES_OFF_PATH,
    "medias_beninois":    DATA_MEDIAS_BENINOIS_PATH,
    "medias_internationaux":DATA_MEDIAS_INTERNATIONAUX_PATH,
}


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

def validate(df: pd.DataFrame, label: str, schema: dict) -> dict:
    """
    Valide un DataFrame contre son schéma.

    Returns:
        dict avec les clés : passed, warnings, errors, stats
    """
    errors   = []
    warnings_list = []
    stats    = {"rows": len(df), "cols": len(df.columns)}

    # 1. Colonnes requises présentes
    missing_cols = [c for c in schema["required_cols"] if c not in df.columns]
    if missing_cols:
        errors.append(f"Colonnes manquantes : {missing_cols}")

    # 2. Nulls sur colonnes critiques
    for col in schema["non_null_cols"]:
        if col not in df.columns:
            continue
        null_count = df[col].isna().sum()
        if null_count > 0:
            pct = round(null_count / len(df) * 100, 1)
            if pct > 10:
                errors.append(f"Colonne critique '{col}' : {null_count} nulls ({pct}%)")
            else:
                warnings_list.append(f"Colonne '{col}' : {null_count} nulls ({pct}%)")

    # 3. Plage de dates cohérente
    date_col = schema.get("date_col")
    if date_col and date_col in df.columns:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        valid_dates = dates.dropna()
        if len(valid_dates):
            d_min = valid_dates.min().strftime("%Y-%m-%d")
            d_max = valid_dates.max().strftime("%Y-%m-%d")
            stats["date_range"] = f"{d_min} → {d_max}"
            # Alerte si des dates futures aberrantes
            future = (valid_dates > pd.Timestamp.now()).sum()
            if future:
                warnings_list.append(f"{future} dates futures détectées")

    # 4. Validation bbox GPS
    if schema.get("has_geo") and "ActionGeo_Lat" in df.columns:
        bb = BENIN_BBOX
        hors_bbox = df[
            (df["ActionGeo_Lat"]  < bb["lat_min"]) | (df["ActionGeo_Lat"]  > bb["lat_max"]) |
            (df["ActionGeo_Long"] < bb["lon_min"]) | (df["ActionGeo_Long"] > bb["lon_max"])
        ]
        if len(hors_bbox):
            warnings_list.append(f"{len(hors_bbox)} points hors bbox Bénin — filtrés automatiquement")
            stats["geo_filtered"] = len(hors_bbox)

    # 5. Dataset vide
    if len(df) == 0:
        errors.append("Dataset vide — aucune ligne après transformation")

    passed = len(errors) == 0
    return {
        "passed":   passed,
        "errors":   errors,
        "warnings": warnings_list,
        "stats":    stats,
    }


def filter_bbox(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les points GPS hors de la bounding box du Bénin."""
    bb = BENIN_BBOX
    mask = (
        (df["ActionGeo_Lat"]  >= bb["lat_min"]) & (df["ActionGeo_Lat"]  <= bb["lat_max"]) &
        (df["ActionGeo_Long"] >= bb["lon_min"]) & (df["ActionGeo_Long"] <= bb["lon_max"])
    )
    return df[mask].reset_index(drop=True)


# ---------------------------------------------------------------------------
# EXPORT
# ---------------------------------------------------------------------------

def export_csv(df: pd.DataFrame, label: str) -> Path:
    """Sauvegarde en CSV dans data/processed/."""
    DIR_CSV.mkdir(parents=True, exist_ok=True)
    path = DIR_CSV / f"{label}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    logger.info(f"  [CSV]     {path} — {len(df)} lignes")
    return path


def export_parquet(df: pd.DataFrame, label: str) -> Path | None:
    """
    Sauvegarde en Parquet si le dataset dépasse PARQUET_MIN_ROWS.
    Convertit les colonnes datetime en string ISO pour compatibilité maximale.
    """
    if len(df) < PARQUET_MIN_ROWS:
        return None

    DIR_PARQUET.mkdir(parents=True, exist_ok=True)
    path = DIR_PARQUET / f"{label}.parquet"

    df_pq = df.copy()
    for col in df_pq.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
        df_pq[col] = df_pq[col].astype(str)
    # CategoricalDtype → string (Parquet Engine pyarrow gère mal certains CategoricalDtype)
    for col in df_pq.select_dtypes(include=["category"]).columns:
        df_pq[col] = df_pq[col].astype(str)

    df_pq.to_parquet(path, index=False, engine="pyarrow", compression="snappy")
    size_kb = path.stat().st_size // 1024
    logger.info(f"  [PARQUET] {path} — {len(df)} lignes ({size_kb} KB)")
    return path


def export_geojson(df: pd.DataFrame, label: str) -> Path:
    """
    Construit un GeoJSON FeatureCollection depuis un DataFrame avec coordonnées GPS.
    Chaque ligne devient un Feature Point avec toutes les colonnes en propriétés.
    """
    DIR_GEOJSON.mkdir(parents=True, exist_ok=True)
    path = DIR_GEOJSON / f"{label}.geojson"

    features = []
    for _, row in df.iterrows():
        props = {
            k: (v if pd.notna(v) else None)
            for k, v in row.items()
            if k not in ("ActionGeo_Lat", "ActionGeo_Long")
        }
        # Sérialisation des types non-JSON-natifs
        for k, v in props.items():
            if isinstance(v, (pd.Timestamp,)):
                props[k] = v.isoformat()
            elif hasattr(v, "item"):          # numpy scalar → python natif
                props[k] = v.item()

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row["ActionGeo_Long"]), float(row["ActionGeo_Lat"])],
            },
            "properties": props,
        })

    geojson = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "metadata": {
            "dataset":    label,
            "generated":  datetime.utcnow().isoformat() + "Z",
            "features":   len(features),
        },
        "features": features,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    size_kb = path.stat().st_size // 1024
    logger.info(f"  [GEOJSON] {path} — {len(features)} features ({size_kb} KB)")
    return path


def save_quality_report(report: dict) -> Path:
    """Sauvegarde le rapport qualité en JSON dans reports/."""
    DIR_REPORTS.mkdir(parents=True, exist_ok=True)
    path = DIR_REPORTS / "quality_report.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info(f"  [REPORT]  {path}")
    return path


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------

def run() -> int:
    """
    Charge, valide et exporte tous les datasets transformés.

    Returns:
        0 si toutes les validations passent, 1 si des erreurs critiques existent.
    """
    logger.info("=" * 60)
    logger.info("GDELT Bénin — Pipeline de chargement")
    logger.info("=" * 60)

    quality_report = {
        "generated": datetime.utcnow().isoformat() + "Z",
        "datasets":  {},
    }

    results  = {"success": [], "failed": [], "warned": []}
    has_critical_error = False

    for label, input_path in REGISTRY.items():
        logger.info(f"\n── {label}")

        # Chargement
        p = Path(input_path)
        if not p.exists():
            logger.warning(f"  Fichier introuvable : {input_path} — ignoré")
            results["failed"].append(label)
            quality_report["datasets"][label] = {"status": "missing"}
            continue

        df = pd.read_csv(input_path)

        # Parsing date si présente (après transform, la colonne s'appelle 'date')
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Validation
        schema = SCHEMAS.get(label, {
            "required_cols": [], "non_null_cols": [],
            "has_geo": False, "date_col": None,
        })
        validation = validate(df, label, schema)

        # Filtre bbox GPS si nécessaire
        if schema.get("has_geo") and "ActionGeo_Lat" in df.columns:
            df = filter_bbox(df)

        # Log validation
        if validation["errors"]:
            for err in validation["errors"]:
                logger.error(f"  ✗ {err}")
            has_critical_error = True
            results["failed"].append(label)
        elif validation["warnings"]:
            for w in validation["warnings"]:
                logger.warning(f"  ⚠ {w}")
            results["warned"].append(label)
        else:
            results["success"].append(label)

        # Export CSV
        export_csv(df, label)

        # Export Parquet conditionnel
        export_parquet(df, label)

        # Export GeoJSON si coordonnées GPS présentes
        if (
            schema.get("has_geo")
            and "ActionGeo_Lat" in df.columns
            and "ActionGeo_Long" in df.columns
        ):
            export_geojson(df, label)

        # Rapport qualité
        quality_report["datasets"][label] = {
            "status":     "ok" if validation["passed"] else "error",
            "validation": validation,
        }

    # Rapport qualité global
    quality_report["summary"] = {
        "total":    len(REGISTRY),
        "success":  len(results["success"]),
        "warned":   len(results["warned"]),
        "failed":   len(results["failed"]),
    }
    save_quality_report(quality_report)

    # Rapport final console
    logger.info("\n" + "=" * 60)
    logger.info(f"Chargement terminé")
    logger.info(f"  ✓ Succès  : {len(results['success'])}")
    logger.info(f"  ⚠ Warnings: {len(results['warned'])} — {results['warned']}")
    logger.info(f"  ✗ Échecs  : {len(results['failed'])} — {results['failed']}")
    logger.info("=" * 60)

    return 0 if not has_critical_error else 1