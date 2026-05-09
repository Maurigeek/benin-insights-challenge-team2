"""Service API for media impact prediction."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models import config
from src.models.media.io import save_training_artifacts
from src.models.media.schemas import MediaModelArtifacts
from src.models.media.trainer import train_media_model


def train_and_save_media_model(
    dataframe: pd.DataFrame,
    features: list[str],
    target: str,
    output_dir: str | Path,
    test_size: float = config.MEDIA_MODEL_TEST_SIZE,
    random_state: int = config.MEDIA_MODEL_RANDOM_STATE,
    n_estimators: int = config.MEDIA_MODEL_N_ESTIMATORS,
    model_type: str = "random_forest",
    split_strategy: str = "time",
) -> MediaModelArtifacts:
    """Train a media impact model and persist its artifacts."""
    training_result = train_media_model(
        dataframe=dataframe,
        features=features,
        target=target,
        test_size=test_size,
        random_state=random_state,
        n_estimators=n_estimators,
        model_type=model_type,
        split_strategy=split_strategy,
    )
    return save_training_artifacts(training_result=training_result, output_dir=output_dir)
