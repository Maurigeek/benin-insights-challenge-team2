from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.models.baseline_anomaly import detect_anomalies_iqr


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


def _validate_contamination(contamination: float | str) -> None:
    """Validate contamination at function boundary."""
    if contamination == "auto":
        return
    if not isinstance(contamination, float):
        raise ValueError("contamination must be a float in (0, 0.5] or 'auto'.")
    if contamination <= 0 or contamination > 0.5:
        raise ValueError("contamination must be in the interval (0, 0.5].")


def _validate_dataframe(dataframe: pd.DataFrame, feature_columns: Sequence[str]) -> list[str]:
    """Validate dataframe and feature columns before model fit."""
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
    if not np.isfinite(numeric.to_numpy()).all():
        raise ValueError("feature columns must contain finite numeric values only.")

    return list(feature_columns)


def detect_anomalies(
    dataframe: pd.DataFrame,
    feature_columns: Sequence[str],
    contamination: float | str = "auto",
    random_state: int = 42,
    n_estimators: int = 200,
    scale_features: bool = True,
) -> AnomalyDetectionResult:
    """Fit Isolation Forest and return enriched dataframe.

    Parameters
    ----------
    dataframe:
        Input dataframe that contains model features.
    feature_columns:
        Ordered list of numeric feature columns used by the model.
    contamination:
        Expected anomaly ratio in (0, 0.5], or ``"auto"``.
    random_state:
        Random seed for deterministic reproducibility.
    n_estimators:
        Number of trees in the Isolation Forest.
    scale_features:
        Whether to standardize features before training.

    Raises
    ------
    ValueError
        If inputs are invalid or features contain null/non-numeric values.
    """
    _validate_contamination(contamination=contamination)
    validated_columns = _validate_dataframe(dataframe=dataframe, feature_columns=feature_columns)

    X = dataframe.loc[:, validated_columns].apply(pd.to_numeric, errors="raise")

    if scale_features:
        scaler = StandardScaler()
        model_input = scaler.fit_transform(X)
    else:
        model_input = X.to_numpy()

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=n_estimators,
    )

    predictions = model.fit_predict(model_input)
    anomaly_score = -model.score_samples(model_input)
    decision_function = model.decision_function(model_input)

    enriched = dataframe.copy()
    enriched["iso_prediction"] = predictions
    enriched["is_anomaly"] = predictions == -1
    enriched["anomaly_score"] = anomaly_score
    enriched["decision_function"] = decision_function

    return AnomalyDetectionResult(
        model=model,
        dataframe=enriched,
        feature_columns=validated_columns,
    )


def build_monthly_anomaly_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate event-level rows into monthly anomaly features."""
    required_columns = ["AvgTone", "GoldsteinScale"]
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required feature columns: {missing}.")

    working = dataframe.copy()
    if "date" in working.columns:
        working["date"] = pd.to_datetime(working["date"], errors="coerce")
        if working["date"].isnull().any():
            raise ValueError("date column must contain valid datetimes.")
        working["year_month"] = working["date"].dt.to_period("M").astype(str)
    elif "year_month" not in working.columns:
        raise ValueError("dataframe must contain either 'date' or 'year_month'.")

    if "NumArticles" not in working.columns:
        working["NumArticles"] = 1

    monthly = (
        working.groupby("year_month", as_index=False)
        .agg(
            rows=("AvgTone", "size"),
            avg_tone=("AvgTone", "mean"),
            goldstein_scale=("GoldsteinScale", "mean"),
            num_articles=("NumArticles", "sum"),
        )
        .dropna()
        .sort_values("year_month")
        .reset_index(drop=True)
    )

    if monthly.empty:
        raise ValueError("monthly aggregation must not be empty.")

    return monthly


def detect_monthly_anomalies(
    dataframe: pd.DataFrame,
    contamination: float = 0.1,
    random_state: int = 42,
) -> MonthlyAnomalyResult:
    """Detect anomalies on monthly aggregates with a stable fallback for small samples."""
    monthly = build_monthly_anomaly_features(dataframe)
    feature_columns = ["rows", "avg_tone", "goldstein_scale", "num_articles"]

    if len(monthly) < 8:
        baseline = detect_anomalies_iqr(
            dataframe=monthly,
            feature_columns=feature_columns,
        )
        enriched = baseline.dataframe.copy()
        enriched["is_anomaly"] = enriched["iqr_is_anomaly"].astype(bool)
        enriched["anomaly_score"] = enriched["iqr_outlier_count"].astype(float)
        return MonthlyAnomalyResult(
            dataframe=enriched,
            feature_columns=feature_columns,
            method="iqr",
        )

    result = detect_anomalies(
        dataframe=monthly,
        feature_columns=feature_columns,
        contamination=contamination,
        random_state=random_state,
    )
    return MonthlyAnomalyResult(
        dataframe=result.dataframe,
        feature_columns=feature_columns,
        method="isolation_forest",
    )
