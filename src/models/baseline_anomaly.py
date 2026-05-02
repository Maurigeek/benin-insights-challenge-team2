from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BaselineAnomalyResult:
    """Output contract for the anomaly baseline."""

    dataframe: pd.DataFrame
    feature_columns: list[str]


def _validate_dataframe(dataframe: pd.DataFrame, feature_columns: Sequence[str]) -> list[str]:
    """Validate input dataframe before baseline scoring."""
    if dataframe.empty:
        raise ValueError("dataframe must not be empty.")
    if not feature_columns:
        raise ValueError("feature_columns must contain at least one column.")

    missing_columns = [column for column in feature_columns if column not in dataframe.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required feature columns: {missing}.")

    selected = dataframe.loc[:, feature_columns]
    if selected.isnull().any().any():
        raise ValueError("feature columns must not contain null values.")

    numeric = selected.apply(pd.to_numeric, errors="raise")
    if numeric.empty:
        raise ValueError("feature columns must contain numeric values.")

    return list(feature_columns)


def detect_anomalies_iqr(
    dataframe: pd.DataFrame,
    feature_columns: Sequence[str],
    multiplier: float = 1.5,
) -> BaselineAnomalyResult:
    """Flag rows outside a robust IQR envelope.

    The baseline marks a row anomalous when at least one feature falls outside
    the [Q1 - multiplier * IQR, Q3 + multiplier * IQR] interval.
    """
    if multiplier <= 0:
        raise ValueError("multiplier must be strictly positive.")

    validated_columns = _validate_dataframe(dataframe=dataframe, feature_columns=feature_columns)
    numeric = dataframe.loc[:, validated_columns].apply(pd.to_numeric, errors="raise")

    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr

    is_anomaly = numeric.lt(lower_bound) | numeric.gt(upper_bound)
    anomaly_flag = is_anomaly.any(axis=1)

    enriched = dataframe.copy()
    enriched["iqr_is_anomaly"] = anomaly_flag
    enriched["iqr_outlier_count"] = is_anomaly.sum(axis=1)

    return BaselineAnomalyResult(dataframe=enriched, feature_columns=validated_columns)
