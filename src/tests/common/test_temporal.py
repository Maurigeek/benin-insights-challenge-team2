from __future__ import annotations

import unittest

import pandas as pd

from src.models.common.temporal import add_year_month, build_month_coverage


class TemporalHelpersTests(unittest.TestCase):
    def test_add_year_month_creates_period_column(self) -> None:
        dataframe = pd.DataFrame({"date": ["2026-01-05", "2026-02-14"]})

        enriched = add_year_month(dataframe)

        self.assertIn("year_month", enriched.columns)
        self.assertEqual(enriched["year_month"].tolist(), ["2026-01", "2026-02"])

    def test_build_month_coverage_flags_partial_edge_months(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2026-01-05", "2026-01-14", "2026-02-03", "2026-02-20"],
            }
        )

        coverage = build_month_coverage(dataframe)

        self.assertEqual(coverage.loc[0, "year_month"], "2026-01")
        self.assertTrue(bool(coverage.loc[0, "is_partial_month"]))
        self.assertEqual(int(coverage.loc[0, "expected_days"]), 27)
        self.assertEqual(int(coverage.loc[0, "observed_days"]), 2)

        self.assertEqual(coverage.loc[1, "year_month"], "2026-02")
        self.assertTrue(bool(coverage.loc[1, "is_partial_month"]))
        self.assertEqual(int(coverage.loc[1, "expected_days"]), 20)
        self.assertEqual(int(coverage.loc[1, "observed_days"]), 2)

    def test_build_month_coverage_marks_full_internal_month(self) -> None:
        dataframe = pd.DataFrame(
            {
                "date": ["2026-01-05", "2026-02-01", "2026-02-18", "2026-03-20"],
            }
        )

        coverage = build_month_coverage(dataframe)
        february = coverage.loc[coverage["year_month"] == "2026-02"].iloc[0]

        self.assertFalse(bool(february["is_partial_month"]))
        self.assertEqual(int(february["expected_days"]), 28)
        self.assertEqual(int(february["observed_days"]), 2)


if __name__ == "__main__":
    unittest.main()
