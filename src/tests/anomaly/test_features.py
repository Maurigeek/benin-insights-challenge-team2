"""Tests for anomaly feature engineering."""

from __future__ import annotations

import unittest

import pandas as pd

from src.models.anomaly import build_monthly_anomaly_features


class AnomalyFeatureTests(unittest.TestCase):
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
        self.assertIn("is_partial_month", monthly.columns)


class PartialMonthFeatureTests(unittest.TestCase):
    def test_partial_month_flag_is_present(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2025-01-15", "2025-01-31", "2025-02-15"],
                "AvgTone": [0.5, 0.5, 0.5],
                "GoldsteinScale": [1.0, 1.0, 1.0],
            }
        )

        monthly = build_monthly_anomaly_features(dataframe)

        self.assertIn("is_partial_month", monthly.columns)
        self.assertTrue(bool(monthly.loc[0, "is_partial_month"]))
        self.assertTrue(bool(monthly.loc[1, "is_partial_month"]))

    def test_complete_month_not_flagged_as_partial(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": pd.date_range("2025-02-01", "2025-02-28", freq="D"),
                "AvgTone": [0.5] * 28,
                "GoldsteinScale": [1.0] * 28,
            }
        )

        monthly = build_monthly_anomaly_features(dataframe)

        self.assertEqual(len(monthly), 1)
        self.assertFalse(bool(monthly.loc[0, "is_partial_month"]))

    def test_observed_vs_expected_days_tracked(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-05", "2025-01-10"],
                "AvgTone": [0.5, 0.5, 0.5],
                "GoldsteinScale": [1.0, 1.0, 1.0],
            }
        )

        monthly = build_monthly_anomaly_features(dataframe)

        self.assertIn("observed_days", monthly.columns)
        self.assertIn("expected_days", monthly.columns)
        self.assertEqual(int(monthly.loc[0, "observed_days"]), 3)
        self.assertGreater(int(monthly.loc[0, "expected_days"]), 3)


if __name__ == "__main__":
    unittest.main()
