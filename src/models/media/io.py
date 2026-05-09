"""Persistence helpers for media impact models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib

from src.models.media.schemas import MediaModelArtifacts, MediaTrainingResult


def save_training_artifacts(
    training_result: MediaTrainingResult,
    output_dir: str | Path,
) -> MediaModelArtifacts:
    """Persist model artifacts to disk."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    model_path = out / "media_rf.pkl"
    encoder_path = out / "media_encoders.joblib"
    metrics_path = out / "media_metrics.json"

    joblib.dump(training_result.model, model_path)
    joblib.dump(training_result.metadata, encoder_path)
    metrics_path.write_text(json.dumps(training_result.metrics, indent=2), encoding="utf-8")

    return MediaModelArtifacts(
        model_path=model_path,
        encoder_path=encoder_path,
        metrics_path=metrics_path,
    )


def load_model(model_path: str | Path) -> Any:
    """Load a persisted media model pipeline."""
    return joblib.load(model_path)
