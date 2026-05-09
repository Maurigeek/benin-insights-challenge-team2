"""Post-processing for anomaly detection outputs."""

from __future__ import annotations

import pandas as pd


def add_method_metadata(dataframe: pd.DataFrame, method: str) -> pd.DataFrame:
    """Attach the detector method to the output dataframe."""
    enriched = dataframe.copy()
    enriched["method"] = method
    return enriched


def apply_partial_month_handling(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Flag partial months and prevent them from being scored as anomalies."""
    enriched = dataframe.copy()
    if "is_partial_month" not in enriched.columns:
        enriched["is_partial_month"] = False

    enriched["is_partial_signal"] = enriched["is_partial_month"].astype(bool)
    if "is_anomaly" in enriched.columns:
        enriched.loc[enriched["is_partial_signal"], "is_anomaly"] = False

    return enriched
