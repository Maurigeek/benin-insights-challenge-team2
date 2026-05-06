from __future__ import annotations

from pathlib import Path
import joblib
from dataclasses import dataclass
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


@dataclass
class MediaModelArtifacts:
    model_path: Path
    encoder_path: Path


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
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    df_local = df.copy()
    df_local = df_local[features + [target]].dropna()

    # Encode categorical if present
    encoders: dict[str, LabelEncoder] = {}
    for col in features:
        if df_local[col].dtype == object or df_local[col].dtype.name == "category":
            le = LabelEncoder()
            df_local[col] = le.fit_transform(df_local[col].astype(str))
            encoders[col] = le

    X = df_local[features]
    y = df_local[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    model = RandomForestClassifier(n_estimators=200, random_state=random_state)
    model.fit(X_train, y_train)

    # Evaluate briefly
    preds = model.predict(X_test)
    report = classification_report(y_test, preds)
    print(report)

    model_path = out / "media_rf.pkl"
    encoder_path = out / "media_encoders.joblib"

    joblib.dump(model, model_path)
    joblib.dump(encoders, encoder_path)

    return MediaModelArtifacts(model_path=model_path, encoder_path=encoder_path)


def load_model(model_path: str | Path):
    return joblib.load(model_path)
