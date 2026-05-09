"""Schemas for media impact prediction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MediaTrainingResult:
    """In-memory result of training a media model."""

    model: Any
    metrics: dict[str, Any]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class MediaModelArtifacts:
    """File artifacts produced by training."""

    model_path: Path
    encoder_path: Path
    metrics_path: Path
