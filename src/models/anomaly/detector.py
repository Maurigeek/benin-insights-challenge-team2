"""Detection algorithms for anomalies."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.models import config
from src.models.anomaly.schemas import AnomalyDetectionResult


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
    random_state: int = config.DEFAULT_RANDOM_STATE,
    n_estimators: int = config.DEFAULT_N_ESTIMATORS,
    scale_features: bool = True,
) -> AnomalyDetectionResult:
    """Fit Isolation Forest and return enriched dataframe."""
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
