# Configuration centrale du projet

# Période d'analyse
YEAR_START = 2025
DATE_START = "20250101"
DATE_END   = "20260428"

# Filtres GDELT
COUNTRY_CODE_ACTION = "BN"   # Bénin comme lieu d'action
COUNTRY_CODE_ACTOR  = "BEN"  # Bénin comme acteur principal

# BigQuery
BQ_TABLE   = "gdelt-bq.gdeltv2.events"
BQ_LIMIT   = 10000

# Colonnes à extraire
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
    "SOURCEURL"
]

# Chemins fichiers
DATA_RAW_PATH       = "data/raw/gdelt_benin_main.csv"
DATA_TONE_PATH      = "data/processed/tone_monthly.csv"
DATA_ACTORS_PATH    = "data/processed/actors_country.csv"
DATA_EVENTS_PATH    = "data/processed/events_by_type.csv"
DATA_GEO_PATH       = "data/processed/geo_events.csv"