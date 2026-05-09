"""Feature engineering for anomaly detection."""

from __future__ import annotations

import pandas as pd

from src.models import config
from src.models.common.temporal import add_year_month, build_month_coverage


def build_monthly_anomaly_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate event-level rows into monthly anomaly features."""
    missing_columns = [
        column
        for column in config.REQUIRED_EVENT_COLUMNS
        if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required feature columns: {missing}.")

    working = dataframe.copy()
    if config.DATE_COLUMN in working.columns:
        working = add_year_month(working, date_column=config.DATE_COLUMN)
    elif config.YEAR_MONTH_COLUMN not in working.columns:
        raise ValueError("dataframe must contain either 'date' or 'year_month'.")

    if config.NUM_ARTICLES_COLUMN not in working.columns:
        working[config.NUM_ARTICLES_COLUMN] = 1

    monthly = (
        working.groupby(config.YEAR_MONTH_COLUMN, as_index=False)
        .agg(
            rows=(config.REQUIRED_EVENT_COLUMNS[0], "size"),
            avg_tone=(config.REQUIRED_EVENT_COLUMNS[0], "mean"),
            goldstein_scale=(config.REQUIRED_EVENT_COLUMNS[1], "mean"),
            num_articles=(config.NUM_ARTICLES_COLUMN, "sum"),
        )
        .dropna()
        .sort_values(config.YEAR_MONTH_COLUMN)
        .reset_index(drop=True)
    )

    if config.DATE_COLUMN in working.columns:
        coverage = build_month_coverage(working, date_column=config.DATE_COLUMN)
        monthly = monthly.merge(coverage, on=config.YEAR_MONTH_COLUMN, how="left")

    if monthly.empty:
        raise ValueError("monthly aggregation must not be empty.")

    return monthly
