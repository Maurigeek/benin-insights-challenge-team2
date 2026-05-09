"""Output contracts for anomaly detection."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass(frozen=True)
class AnomalyDetectionResult:
    """Output contract for anomaly detection."""

    model: IsolationForest
    dataframe: pd.DataFrame
    feature_columns: list[str]


@dataclass(frozen=True)
class MonthlyAnomalyResult:
    """Output contract for monthly anomaly detection."""

    dataframe: pd.DataFrame
    feature_columns: list[str]
    method: str
