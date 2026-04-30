import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# PÉRIODE D'ANALYSE
YEAR_START = os.getenv("YEAR_START", 2025)
DATE_START = os.getenv("DATE_START", "20250101")
DATE_END   = os.getenv("DATE_END", "20260428")  

# FILTRES GDELT
COUNTRY_CODE_ACTION = os.getenv("COUNTRY_CODE_ACTION", "BN")    # Bénin comme lieu d'action
COUNTRY_CODE_ACTOR  = os.getenv("COUNTRY_CODE_ACTOR", "BEN")   # Bénin comme acteur principal

# BIGQUERY TABLE AND LIMIT
BQ_TABLE = os.getenv("BQ_TABLE", "gdelt-bq.gdeltv2.events")
BQ_LIMIT = os.getenv("BQ_LIMIT", 10000)

USE_BIGQUERY = os.getenv("USE_BIGQUERY", "false").lower() == "true"

# COLONNES À EXTRAIRE
COLUMNS = [
    "SQLDATE",
    "Actor1Name",
    "Actor1CountryCode",
    "Actor2Name",
    "Actor2CountryCode",
    "EventCode",
    "EventBaseCode",
    "EventRootCode",
    "GoldsteinScale",
    "NumArticles",
    "AvgTone",
    "ActionGeo_FullName",
    "ActionGeo_CountryCode",
    "ActionGeo_Lat",
    "ActionGeo_Long",
    "SOURCEURL",
]

# CHEMINS FICHIERS — RAW
DATA_RAW_PATH       = BASE_DIR / os.getenv("DATA_RAW_PATH",     "data/raw/gdelt_benin_main.csv")
DATA_RAW_GEO_PATH   = BASE_DIR / os.getenv("DATA_RAW_GEO_PATH", "data/raw/geo_events.csv")    

# CHEMINS FICHIERS — PROCESSED 
DATA_CLEAN_PATH             = BASE_DIR / os.getenv("DATA_CLEAN_PATH",             "data/processed/gdelt_benin_clean.csv")
DATA_TONE_PATH              = BASE_DIR / os.getenv("DATA_TONE_PATH",              "data/processed/tone_monthly.csv")
DATA_ACTORS_PATH            = BASE_DIR / os.getenv("DATA_ACTORS_PATH",            "data/processed/actors_country.csv")
DATA_EVENTS_PATH            = BASE_DIR / os.getenv("DATA_EVENTS_PATH",            "data/processed/events_by_type.csv")
DATA_GEO_PATH               = BASE_DIR / os.getenv("DATA_GEO_PATH",               "data/processed/geo_events.csv")
DATA_ZOOM_DEC2025_PATH      = BASE_DIR / os.getenv("DATA_ZOOM_DEC2025_PATH",      "data/processed/zoom_dec2025.csv")
DATA_ZOOM_ELECTION_PATH     = BASE_DIR / os.getenv("DATA_ZOOM_ELECTION_PATH",     "data/processed/zoom_election2026.csv")
DATA_CULTURE_PATH           = BASE_DIR / os.getenv("DATA_CULTURE_PATH",           "data/processed/culture_tourisme.csv")
DATA_COOPERATION_NGA_PATH   = BASE_DIR / os.getenv("DATA_COOPERATION_NGA_PATH",   "data/processed/cooperation_ben_nga.csv")
DATA_SECURITE_NORD_PATH     = BASE_DIR / os.getenv("DATA_SECURITE_NORD_PATH",     "data/processed/securite_nord.csv")
DATA_FEMMES_PATH            = BASE_DIR / os.getenv("DATA_FEMMES_PATH",            "data/processed/femmes_benin.csv")
DATA_CHINE_PATH             = BASE_DIR / os.getenv("DATA_CHINE_PATH",             "data/processed/chine_benin.csv")
DATA_PERSO_BENIN_PATH       = BASE_DIR / os.getenv("DATA_PERSO_BENIN_PATH",       "data/processed/personnalites_benin.csv")
DATA_PERSO_ETRANGERES_PATH  = BASE_DIR / os.getenv("DATA_PERSO_ETRANGERES_PATH",  "data/processed/personnalites_etrangeres.csv")
DATA_LIBERTE_PRESSE_PATH    = BASE_DIR / os.getenv("DATA_LIBERTE_PRESSE_PATH",    "data/processed/liberte_presse.csv")