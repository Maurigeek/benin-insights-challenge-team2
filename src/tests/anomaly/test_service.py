"""Tests for anomaly service layer."""

from __future__ import annotations

import unittest

import pandas as pd

from src.models.anomaly import MonthlyAnomalyResult, detect_monthly_anomalies


class AnomalyServiceTests(unittest.TestCase):
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


class PartialMonthHandlingTests(unittest.TestCase):
    def test_partial_month_not_flagged_as_anomaly_due_to_incompleteness(self) -> None:
        normal_data = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-02", "2025-01-31", freq="D"),
                "AvgTone": [0.5] * 30,
                "GoldsteinScale": [1.0] * 30,
                "NumArticles": [100] * 30,
            }
        )

        partial_first = pd.DataFrame(
            {
                "date": ["2024-12-31"],
                "AvgTone": [0.5],
                "GoldsteinScale": [1.0],
                "NumArticles": [100],
            }
        )

        dataframe = pd.concat([partial_first, normal_data], ignore_index=True)
        result = detect_monthly_anomalies(dataframe)

        monthly = result.dataframe
        partial_month_row = monthly.loc[monthly["year_month"] == "2024-12"].iloc[0]

        self.assertTrue(bool(partial_month_row["is_partial_month"]))

    def test_small_sample_with_partial_months_uses_fallback(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-02-15", "2025-03-28"],
                "AvgTone": [0.1, 0.2, 10.0],
                "GoldsteinScale": [1.0, 1.0, 5.0],
                "NumArticles": [50, 75, 200],
            }
        )

        result = detect_monthly_anomalies(dataframe)

        self.assertEqual(result.method, "iqr")
        self.assertIn("is_anomaly", result.dataframe.columns)

    def test_partial_months_not_marked_as_anomalies(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2025-01-15", "2025-01-20", "2025-02-15"],
                "AvgTone": [0.5, 0.5, -10.0],
                "GoldsteinScale": [1.0, 1.0, 8.0],
                "NumArticles": [100, 100, 1000],
            }
        )

        result = detect_monthly_anomalies(dataframe)
        monthly = result.dataframe

        partial_months = monthly[monthly["is_partial_month"]]

        self.assertTrue((partial_months["is_anomaly"] == False).all())
        self.assertTrue((partial_months["is_partial_signal"] == True).all())

    def test_complete_months_can_be_anomalies(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", "2025-12-31", freq="D"),
                "AvgTone": [0.5] * 365,
                "GoldsteinScale": [1.0] * 365,
                "NumArticles": [100] * 365,
            }
        )

        spike_dates = pd.date_range("2025-06-01", "2025-06-30", freq="D").tolist()
        spike_mask = dataframe["date"].isin(spike_dates)
        dataframe.loc[spike_mask, "AvgTone"] = -10.0
        dataframe.loc[spike_mask, "GoldsteinScale"] = 8.0
        dataframe.loc[spike_mask, "NumArticles"] = 1000

        result = detect_monthly_anomalies(dataframe)
        monthly = result.dataframe

        june = monthly[monthly["year_month"] == "2025-06"].iloc[0]
        self.assertFalse(bool(june["is_partial_month"]))
        self.assertTrue(bool(june["is_anomaly"]))
        self.assertFalse(bool(june["is_partial_signal"]))

    def test_output_has_partial_signal_column(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2025-01-15", "2025-02-01", "2025-02-28", "2025-03-15"],
                "AvgTone": [0.5, 0.5, 0.5, 0.5],
                "GoldsteinScale": [1.0, 1.0, 1.0, 1.0],
                "NumArticles": [100, 100, 100, 100],
            }
        )

        result = detect_monthly_anomalies(dataframe)

        self.assertIn("is_partial_signal", result.dataframe.columns)
        n_signals = int(result.dataframe["is_partial_signal"].sum())
        n_anomalies = int(result.dataframe["is_anomaly"].sum())
        self.assertLessEqual(n_signals + n_anomalies, len(result.dataframe))


if __name__ == "__main__":
    unittest.main()
