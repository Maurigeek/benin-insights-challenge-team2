"""Unit tests for topic_model module."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from src.models.topic_model import (
    TopicExtractionResult,
    _normalize_texts,
    _validate_hyperparameters,
    extract_topics,
)


class _FakeTopicModel:
    def fit_transform(self, text_list: list[str]) -> tuple[list[int], list[float]]:
        topics = [index % 2 for index, _ in enumerate(text_list)]
        probabilities = [0.9 for _ in text_list]
        return topics, probabilities


class TopicModelTests(unittest.TestCase):
    def test_normalize_texts_removes_empty_values(self) -> None:
        normalized = _normalize_texts([" alpha ", "", "  ", "beta"])
        self.assertEqual(normalized, ["alpha", "beta"])

    def test_normalize_texts_raises_on_empty_input(self) -> None:
        with self.assertRaises(ValueError):
            _normalize_texts(["", "   "])

    def test_validate_hyperparameters_accepts_valid_values(self) -> None:
        _validate_hyperparameters(min_topic_size=10, nr_topics="auto")
        _validate_hyperparameters(min_topic_size=10, nr_topics=5)

    def test_validate_hyperparameters_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            _validate_hyperparameters(min_topic_size=1, nr_topics="auto")
        with self.assertRaises(ValueError):
            _validate_hyperparameters(min_topic_size=10, nr_topics=0)
        with self.assertRaises(ValueError):
            _validate_hyperparameters(min_topic_size=10, nr_topics="bad")

    def test_extract_topics_returns_contract(self) -> None:
        fake_model = _FakeTopicModel()
        texts = ["politique benin", "securite frontaliere", "cooperation regionale"]

        with patch("src.models.topic_model._build_topic_model", return_value=fake_model):
            result = extract_topics(texts=texts, min_topic_size=3, nr_topics="auto")

        self.assertIsInstance(result, TopicExtractionResult)
        self.assertEqual(len(result.topics), len(texts))
        self.assertEqual(len(result.probabilities or []), len(texts))

    def test_extract_topics_raises_with_invalid_texts(self) -> None:
        fake_model = _FakeTopicModel()
        with patch("src.models.topic_model._build_topic_model", return_value=fake_model):
            with self.assertRaises(ValueError):
                extract_topics(texts=["", "  "], min_topic_size=3, nr_topics="auto")


if __name__ == "__main__":
    unittest.main()
