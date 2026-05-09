"""Shared configuration for ML models."""

DEFAULT_CONTAMINATION = 0.15
DEFAULT_RANDOM_STATE = 42
DEFAULT_N_ESTIMATORS = 200
MIN_MONTHS_FOR_IFOREST = 8

MONTHLY_FEATURE_COLUMNS = [
    "rows",
    "avg_tone",
    "goldstein_scale",
    "num_articles",
]

REQUIRED_EVENT_COLUMNS = [
    "AvgTone",
    "GoldsteinScale",
]

NUM_ARTICLES_COLUMN = "NumArticles"
YEAR_MONTH_COLUMN = "year_month"
DATE_COLUMN = "date"

MEDIA_MODEL_TEST_SIZE = 0.2
MEDIA_MODEL_RANDOM_STATE = 42
MEDIA_MODEL_N_ESTIMATORS = 200

MEDIA_SOURCE_COLUMN = "SOURCEURL"
MEDIA_DATE_COLUMN = "date"
MEDIA_LABEL_COLUMN = "media_label"
MEDIA_BENIN_SOURCES_PATH = "data/processed/medias_beninois.csv"
MEDIA_INTERNATIONAL_SOURCES_PATH = "data/processed/medias_internationaux.csv"

MEDIA_DEFAULT_FEATURES = [
    "EventRootCode",
    "EventBaseCode",
    "GoldsteinScale",
    "AvgTone",
    "ActionGeo_CountryCode",
    "Actor1CountryCode",
    "Actor2CountryCode",
    "mois",
    "sentiment",
]
