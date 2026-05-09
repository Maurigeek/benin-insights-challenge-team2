"""Feature preparation for media impact prediction."""

from __future__ import annotations

import pandas as pd

from src.models import config


def build_feature_frame(
    dataframe: pd.DataFrame,
    feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Select and validate feature columns for media prediction."""
    columns = feature_columns or list(config.MEDIA_DEFAULT_FEATURES)
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"Missing required feature columns: {missing_list}.")

    return dataframe.loc[:, columns].copy()
