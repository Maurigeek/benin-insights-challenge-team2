"""Service layer for anomaly detection."""

from __future__ import annotations

import pandas as pd

from src.models import config
from src.models.anomaly.detector import detect_anomalies
from src.models.anomaly.features import build_monthly_anomaly_features
from src.models.anomaly.postprocessing import add_method_metadata, apply_partial_month_handling
from src.models.anomaly.schemas import MonthlyAnomalyResult
from src.models.baseline_anomaly import detect_anomalies_iqr


def detect_monthly_anomalies(
    dataframe: pd.DataFrame,
    contamination: float = config.DEFAULT_CONTAMINATION,
    random_state: int = config.DEFAULT_RANDOM_STATE,
) -> MonthlyAnomalyResult:
    """Detect anomalies on monthly aggregates with a stable fallback for small samples."""
    monthly = build_monthly_anomaly_features(dataframe)
    feature_columns = list(config.MONTHLY_FEATURE_COLUMNS)

    if len(monthly) < config.MIN_MONTHS_FOR_IFOREST:
        baseline = detect_anomalies_iqr(
            dataframe=monthly,
            feature_columns=feature_columns,
        )
        enriched = baseline.dataframe.copy()
        enriched["is_anomaly"] = enriched["iqr_is_anomaly"].astype(bool)
        enriched["anomaly_score"] = enriched["iqr_outlier_count"].astype(float)
        enriched = add_method_metadata(enriched, method="iqr")
        enriched = apply_partial_month_handling(enriched)
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
    enriched = add_method_metadata(result.dataframe, method="isolation_forest")
    enriched = apply_partial_month_handling(enriched)
    return MonthlyAnomalyResult(
        dataframe=enriched,
        feature_columns=feature_columns,
        method="isolation_forest",
    )
