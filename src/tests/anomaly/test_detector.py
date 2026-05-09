"""Tests for anomaly detectors."""

from __future__ import annotations

import unittest

import pandas as pd

from src.models.anomaly import AnomalyDetectionResult, detect_anomalies


class AnomalyDetectorTests(unittest.TestCase):
    def test_detect_anomalies_returns_contract(self) -> None:
        dataframe = pd.DataFrame(
            {
                "AvgTone": [0.1, 0.2, 0.0, -0.1],
                "GoldsteinScale": [1.0, 0.8, 1.1, 0.9],
                "NumArticles": [100, 98, 103, 97],
            }
        )

        result = detect_anomalies(
            dataframe=dataframe,
            feature_columns=["AvgTone", "GoldsteinScale", "NumArticles"],
            contamination=0.25,
            random_state=7,
        )

        self.assertIsInstance(result, AnomalyDetectionResult)
        self.assertEqual(len(result.dataframe), len(dataframe))
        self.assertIn("iso_prediction", result.dataframe.columns)
        self.assertIn("is_anomaly", result.dataframe.columns)
        self.assertIn("anomaly_score", result.dataframe.columns)
        self.assertIn("decision_function", result.dataframe.columns)

    def test_detect_anomalies_raises_on_missing_feature_columns(self) -> None:
        dataframe = pd.DataFrame({"AvgTone": [0.1], "NumArticles": [10]})

        with self.assertRaises(ValueError):
            detect_anomalies(
                dataframe=dataframe,
                feature_columns=["AvgTone", "GoldsteinScale", "NumArticles"],
            )

    def test_detect_anomalies_raises_on_null_values(self) -> None:
        dataframe = pd.DataFrame(
            {
                "AvgTone": [0.1, None],
                "GoldsteinScale": [1.0, 0.9],
                "NumArticles": [100, 110],
            }
        )

        with self.assertRaises(ValueError):
            detect_anomalies(
                dataframe=dataframe,
                feature_columns=["AvgTone", "GoldsteinScale", "NumArticles"],
            )

    def test_detect_anomalies_raises_on_invalid_contamination(self) -> None:
        dataframe = pd.DataFrame(
            {
                "AvgTone": [0.1, 0.2],
                "GoldsteinScale": [1.0, 0.8],
                "NumArticles": [100, 99],
            }
        )

        with self.assertRaises(ValueError):
            detect_anomalies(
                dataframe=dataframe,
                feature_columns=["AvgTone", "GoldsteinScale", "NumArticles"],
                contamination=0.0,
            )

    def test_detect_anomalies_flags_extreme_outlier(self) -> None:
        normal_rows = pd.DataFrame(
            {
                "AvgTone": [0.1, 0.0, -0.1, 0.2, -0.2] * 6,
                "GoldsteinScale": [1.0, 0.9, 1.1, 0.95, 1.05] * 6,
                "NumArticles": [100, 98, 102, 99, 101] * 6,
            }
        )

        outlier_row = pd.DataFrame(
            {
                "AvgTone": [-12.0],
                "GoldsteinScale": [-8.0],
                "NumArticles": [1400],
            }
        )

        dataframe = pd.concat([normal_rows, outlier_row], ignore_index=True)

        result = detect_anomalies(
            dataframe=dataframe,
            feature_columns=["AvgTone", "GoldsteinScale", "NumArticles"],
            contamination=0.1,
            random_state=7,
        )

        outlier_index = len(dataframe) - 1
        self.assertTrue(bool(result.dataframe.loc[outlier_index, "is_anomaly"]))


if __name__ == "__main__":
    unittest.main()
