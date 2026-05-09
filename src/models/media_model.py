"""Backward-compatible access to the media model package."""

from src.models.media import (  # noqa: F401
    MediaModelArtifacts,
    MediaTrainingResult,
    load_model,
    save_training_artifacts,
    train_and_save_media_model,
    train_media_model,
)

__all__ = [
    "MediaModelArtifacts",
    "MediaTrainingResult",
    "load_model",
    "save_training_artifacts",
    "train_and_save_media_model",
    "train_media_model",
]
