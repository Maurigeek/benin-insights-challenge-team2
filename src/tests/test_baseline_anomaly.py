"""Unit tests for baseline_anomaly module."""

from __future__ import annotations

import unittest

import pandas as pd

from src.models.baseline_anomaly import BaselineAnomalyResult, detect_anomalies_iqr


class BaselineAnomalyTests(unittest.TestCase):
    def test_detect_anomalies_iqr_returns_contract(self) -> None:
        dataframe = pd.DataFrame(
            {
                "rows": [10, 11, 9, 10],
                "avg_tone": [0.1, 0.0, -0.1, 0.2],
                "num_articles": [100, 102, 98, 101],
            }
        )

        result = detect_anomalies_iqr(
            dataframe=dataframe,
            feature_columns=["rows", "avg_tone", "num_articles"],
        )

        self.assertIsInstance(result, BaselineAnomalyResult)
        self.assertIn("iqr_is_anomaly", result.dataframe.columns)
        self.assertIn("iqr_outlier_count", result.dataframe.columns)

    def test_detect_anomalies_iqr_flags_clear_outlier(self) -> None:
        dataframe = pd.DataFrame(
            {
                "rows": [10, 11, 9, 10, 250],
                "avg_tone": [0.1, 0.0, -0.1, 0.2, 9.0],
                "num_articles": [100, 102, 98, 101, 1400],
            }
        )

        result = detect_anomalies_iqr(
            dataframe=dataframe,
            feature_columns=["rows", "avg_tone", "num_articles"],
        )

        self.assertTrue(bool(result.dataframe.loc[4, "iqr_is_anomaly"]))
        self.assertGreater(result.dataframe.loc[4, "iqr_outlier_count"], 0)

    def test_detect_anomalies_iqr_raises_on_invalid_multiplier(self) -> None:
        dataframe = pd.DataFrame({"rows": [1], "avg_tone": [0.0], "num_articles": [10]})

        with self.assertRaises(ValueError):
            detect_anomalies_iqr(
                dataframe=dataframe,
                feature_columns=["rows", "avg_tone", "num_articles"],
                multiplier=0,
            )


if __name__ == "__main__":
    unittest.main()
