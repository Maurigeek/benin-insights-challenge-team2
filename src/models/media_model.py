from __future__ import annotations

import json
from pathlib import Path
import joblib
from dataclasses import dataclass
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


@dataclass
class MediaModelArtifacts:
    model_path: Path
    encoder_path: Path
    metrics_path: Path


def train_and_save_media_model(
    df: pd.DataFrame,
    features: list[str],
    target: str,
    output_dir: str | Path,
    test_size: float = 0.2,
    random_state: int = 42,
) -> MediaModelArtifacts:
    """Train a RandomForest to predict `target` and save model + encoder.

    Simple, well-specified contract for notebook use.
    """
    missing_columns = [column for column in [*features, target] if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for media model: {missing_columns}")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    df_local = df.copy()
    df_local = df_local[features + [target]].dropna()
    if df_local.empty:
        raise ValueError("No training rows available after dropping missing values.")

    X = df_local[features]
    y = df_local[target]
    categorical_features = [
        column for column in features if X[column].dtype == object or X[column].dtype.name == "category"
    ]
    numeric_features = [column for column in features if column not in categorical_features]
    n_classes = int(y.nunique())
    estimated_test_rows = max(1, int(round(len(df_local) * test_size)))
    can_stratify = n_classes > 1 and y.value_counts().min() >= 2 and estimated_test_rows >= n_classes
    stratify = y if can_stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), categorical_features),
            ("numeric", "passthrough", numeric_features),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=200, random_state=random_state)),
        ]
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    report = classification_report(y_test, preds, zero_division=0)
    metrics = classification_report(y_test, preds, output_dict=True, zero_division=0)
    print(report)

    model_path = out / "media_rf.pkl"
    encoder_path = out / "media_encoders.joblib"
    metrics_path = out / "media_metrics.json"

    joblib.dump(model, model_path)
    joblib.dump(
        {
            "categorical_features": categorical_features,
            "numeric_features": numeric_features,
            "features": features,
            "target": target,
        },
        encoder_path,
    )
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return MediaModelArtifacts(
        model_path=model_path,
        encoder_path=encoder_path,
        metrics_path=metrics_path,
    )


def load_model(model_path: str | Path):
    return joblib.load(model_path)
