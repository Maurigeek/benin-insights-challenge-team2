"""Unit tests for anomaly_model module."""

from __future__ import annotations

import unittest

import pandas as pd

from src.models.anomaly_model import (
    AnomalyDetectionResult,
    MonthlyAnomalyResult,
    build_monthly_anomaly_features,
    detect_anomalies,
    detect_monthly_anomalies,
)


class AnomalyModelTests(unittest.TestCase):
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

    def test_build_monthly_anomaly_features_aggregates_by_month(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-15", "2025-02-01"],
                "AvgTone": [1.0, -1.0, 0.5],
                "GoldsteinScale": [2.0, 0.0, 1.0],
                "NumArticles": [10, 20, 30],
            }
        )

        monthly = build_monthly_anomaly_features(dataframe)

        self.assertEqual(len(monthly), 2)
        self.assertEqual(monthly.loc[0, "year_month"], "2025-01")
        self.assertEqual(monthly.loc[0, "rows"], 2)
        self.assertEqual(monthly.loc[0, "num_articles"], 30)

    def test_detect_monthly_anomalies_returns_contract(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=12, freq="MS"),
                "AvgTone": [0.1, 0.2, -0.1, 0.0, 0.3, -0.2, 0.1, 0.2, -0.1, 0.0, 0.3, -0.2],
                "GoldsteinScale": [1.0, 0.8, 1.1, 0.9, 1.2, 0.7, 1.0, 0.8, 1.1, 0.9, 1.2, 0.7],
                "NumArticles": [100, 98, 102, 99, 101, 97, 100, 98, 102, 99, 101, 400],
            }
        )

        result = detect_monthly_anomalies(dataframe)

        self.assertIsInstance(result, MonthlyAnomalyResult)
        self.assertIn("is_anomaly", result.dataframe.columns)
        self.assertIn("anomaly_score", result.dataframe.columns)
        self.assertIn(result.method, {"isolation_forest", "iqr"})


if __name__ == "__main__":
    unittest.main()
