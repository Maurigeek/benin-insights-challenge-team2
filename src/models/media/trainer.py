"""Training logic for media impact prediction."""

from __future__ import annotations

from typing import Any, cast

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from src.models import config
from src.models.media.schemas import MediaTrainingResult


def _validate_columns(dataframe: pd.DataFrame, features: list[str], target: str) -> None:
    missing_columns = [column for column in [*features, target] if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for media model: {missing_columns}")


def _prepare_training_frame(
    dataframe: pd.DataFrame,
    features: list[str],
    target: str,
) -> pd.DataFrame:
    working = dataframe.copy()
    working = working[features + [target]].dropna()
    if working.empty:
        raise ValueError("No training rows available after dropping missing values.")
    return working


def _split_data(
    features: pd.DataFrame,
    target: pd.Series,
    test_size: float,
    random_state: int,
    dates: pd.Series | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    if dates is not None:
        ordering = dates.sort_values().index
        split_index = max(1, int(round(len(ordering) * (1 - test_size))))
        train_idx = ordering[:split_index]
        test_idx = ordering[split_index:]
        return (
            features.loc[train_idx],
            features.loc[test_idx],
            target.loc[train_idx],
            target.loc[test_idx],
        )

    n_classes = int(target.nunique())
    estimated_test_rows = max(1, int(round(len(target) * test_size)))
    can_stratify = n_classes > 1 and target.value_counts().min() >= 2 and estimated_test_rows >= n_classes
    stratify = target if can_stratify else None

    split = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )
    return cast(tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series], tuple(split))


def train_media_model(
    dataframe: pd.DataFrame,
    features: list[str],
    target: str,
    test_size: float = config.MEDIA_MODEL_TEST_SIZE,
    random_state: int = config.MEDIA_MODEL_RANDOM_STATE,
    n_estimators: int = config.MEDIA_MODEL_N_ESTIMATORS,
    model_type: str = "random_forest",
    split_strategy: str = "time",
    date_column: str = config.MEDIA_DATE_COLUMN,
) -> MediaTrainingResult:
    """Train a media impact model and return metrics plus metadata."""
    _validate_columns(dataframe=dataframe, features=features, target=target)
    working = _prepare_training_frame(dataframe=dataframe, features=features, target=target)

    X = working[features]
    y = working[target]

    categorical_features = [
        column for column in features if X[column].dtype == object or X[column].dtype.name == "category"
    ]
    numeric_features = [column for column in features if column not in categorical_features]

    dates = None
    if split_strategy == "time":
        if date_column not in dataframe.columns:
            raise ValueError(f"Missing required date column: {date_column}.")
        dates = pd.to_datetime(dataframe.loc[working.index, date_column], errors="coerce")

    X_train, X_test, y_train, y_test = _split_data(
        features=X,
        target=y,
        test_size=test_size,
        random_state=random_state,
        dates=dates,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                categorical_features,
            ),
            ("numeric", "passthrough", numeric_features),
        ]
    )
    if model_type == "logistic":
        estimator = LogisticRegression(max_iter=1000, class_weight="balanced")
    elif model_type == "random_forest":
        estimator = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    else:
        raise ValueError("model_type must be 'random_forest' or 'logistic'.")

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", estimator),
        ]
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = cast(
        dict[str, Any],
        classification_report(y_test, preds, output_dict=True, zero_division=0),
    )
    metadata: dict[str, Any] = {
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
        "features": features,
        "target": target,
        "test_size": test_size,
        "random_state": random_state,
        "n_estimators": n_estimators,
        "model_type": model_type,
        "split_strategy": split_strategy,
    }

    return MediaTrainingResult(model=model, metrics=metrics, metadata=metadata)
