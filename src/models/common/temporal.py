from __future__ import annotations

from calendar import monthrange

import pandas as pd


def _ensure_datetime(dataframe: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """Return a copy with a validated datetime column."""
    if date_column not in dataframe.columns:
        raise ValueError(f"dataframe must contain '{date_column}'.")

    working = dataframe.copy()
    working[date_column] = pd.to_datetime(working[date_column], errors="coerce")
    if working[date_column].isnull().any():
        raise ValueError(f"{date_column} column must contain valid datetimes.")

    return working


def add_year_month(dataframe: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """Return a dataframe enriched with a canonical year_month column."""
    working = _ensure_datetime(dataframe=dataframe, date_column=date_column)
    working["year_month"] = working[date_column].dt.to_period("M").astype(str)
    return working


def build_month_coverage(dataframe: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """Describe monthly coverage and flag edge months that are partial."""
    working = add_year_month(dataframe=dataframe, date_column=date_column)

    global_start = working[date_column].min().normalize()
    global_end = working[date_column].max().normalize()

    rows: list[dict[str, object]] = []
    for year_month, month_frame in working.groupby("year_month", sort=True):
        month_start = month_frame[date_column].min().to_period("M").to_timestamp().normalize()
        month_end = month_start + pd.offsets.MonthEnd(0)

        effective_start = max(month_start, global_start)
        effective_end = min(month_end, global_end)
        expected_days = (effective_end - effective_start).days + 1
        observed_days = int(month_frame[date_column].dt.normalize().nunique())
        is_partial_month = bool(effective_start > month_start or effective_end < month_end)

        rows.append(
            {
                "year_month": year_month,
                "period_start": effective_start.date().isoformat(),
                "period_end": effective_end.date().isoformat(),
                "observed_days": observed_days,
                "expected_days": int(expected_days),
                "calendar_days": int(monthrange(month_start.year, month_start.month)[1]),
                "is_partial_month": is_partial_month,
            }
        )

    return pd.DataFrame(rows)
