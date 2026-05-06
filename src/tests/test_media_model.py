"""Unit tests for media_model module."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.models.media_model import load_model, train_and_save_media_model


class MediaModelTests(unittest.TestCase):
    def test_train_and_save_media_model_creates_artifacts(self) -> None:
        dataframe = pd.DataFrame(
            {
                "GoldsteinScale": [1.0, -0.5, 0.2, 1.5, -1.2],
                "EventRootCode": ["01", "02", "01", "03", "02"],
                "is_international": [0, 1, 0, 1, 0],
                "is_high_media": [0, 1, 0, 1, 0],
            }
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            artifacts = train_and_save_media_model(
                dataframe,
                features=["GoldsteinScale", "EventRootCode", "is_international"],
                target="is_high_media",
                output_dir=out_dir,
                test_size=0.2,
                random_state=7,
            )

            self.assertTrue(artifacts.model_path.exists())
            self.assertTrue(artifacts.encoder_path.exists())

            model = load_model(artifacts.model_path)
            preds = model.predict(dataframe[["GoldsteinScale", "EventRootCode", "is_international"]])
            self.assertEqual(len(preds), len(dataframe))


if __name__ == "__main__":
    unittest.main()
