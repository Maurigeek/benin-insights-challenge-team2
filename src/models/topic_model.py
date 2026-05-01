from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TopicExtractionResult:
    """Output contract for topic extraction."""

    model: object
    topics: list[int]
    probabilities: list[float] | None


def _normalize_texts(texts: Iterable[str]) -> list[str]:
    """Normalize texts and remove empty values."""
    normalized_texts = [str(text).strip() for text in texts if str(text).strip()]
    if not normalized_texts:
        raise ValueError("texts must contain at least one non-empty document.")
    return normalized_texts


def _validate_hyperparameters(min_topic_size: int, nr_topics: str | int) -> None:
    """Validate BERTopic hyperparameters at the function boundary."""
    if min_topic_size <= 1:
        raise ValueError("min_topic_size must be greater than 1.")
    if not (nr_topics == "auto" or isinstance(nr_topics, int)):
        raise ValueError("nr_topics must be an integer or 'auto'.")
    if isinstance(nr_topics, int) and nr_topics <= 0:
        raise ValueError("nr_topics must be strictly positive when provided as int.")


def _build_topic_model(min_topic_size: int, nr_topics: str | int) -> object:
    """Build BERTopic model while keeping third-party import at boundary."""
    try:
        from bertopic import BERTopic
    except ImportError as import_error:  # pragma: no cover
        raise ImportError(
            "BERTopic is required. Install with: pip install bertopic sentence-transformers umap-learn hdbscan"
        ) from import_error

    return BERTopic(
        language="multilingual",
        min_topic_size=min_topic_size,
        nr_topics=nr_topics,
        calculate_probabilities=True,
        verbose=False,
    )


def extract_topics(
    texts: Iterable[str],
    min_topic_size: int = 20,
    nr_topics: str | int = "auto",
) -> TopicExtractionResult:
    """Train BERTopic and return model outputs with an explicit contract.

    Parameters
    ----------
    texts:
        Iterable of cleaned text documents.
    min_topic_size:
        Minimum number of samples in a topic.
    nr_topics:
        Number of topics after reduction. Use ``"auto"`` for automatic reduction.

    Raises
    ------
    ValueError
        If inputs are empty or hyperparameters are invalid.
    """
    _validate_hyperparameters(min_topic_size=min_topic_size, nr_topics=nr_topics)
    text_list = _normalize_texts(texts=texts)

    topic_model = _build_topic_model(min_topic_size=min_topic_size, nr_topics=nr_topics)
    topics, probabilities = topic_model.fit_transform(text_list)
    return TopicExtractionResult(model=topic_model, topics=topics, probabilities=probabilities)
