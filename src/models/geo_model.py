from __future__ import annotations

import pandas as pd


DEFAULT_BENIN_LAT = 9.5
DEFAULT_BENIN_LON = 2.25


def build_geo_event_points(dataframe: pd.DataFrame, limit: int = 120) -> pd.DataFrame:
    """Aggregate event rows into map-ready geographic points.

    Returns one row per location with:
    - latitude / longitude
    - aggregated event volume
    - average tone
    - dominant event type
    """
    if limit <= 0:
        raise ValueError("limit must be strictly positive.")

    required_columns = ["ActionGeo_Lat", "ActionGeo_Long", "AvgTone"]
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required geographic columns: {missing}.")

    working = dataframe.copy()
    working["ActionGeo_Lat"] = pd.to_numeric(working["ActionGeo_Lat"], errors="coerce")
    working["ActionGeo_Long"] = pd.to_numeric(working["ActionGeo_Long"], errors="coerce")
    working = working.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long", "AvgTone"])

    # Drop generic country-centroid rows, which visually pollute the map.
    working = working.loc[
        ~(
            working["ActionGeo_Lat"].round(4).eq(DEFAULT_BENIN_LAT)
            & working["ActionGeo_Long"].round(4).eq(DEFAULT_BENIN_LON)
        )
    ].copy()

    if working.empty:
        return pd.DataFrame(
            columns=[
                "location",
                "lat",
                "lon",
                "event_count",
                "avg_tone",
                "dominant_event",
            ]
        )

    if "ActionGeo_FullName" not in working.columns:
        working["ActionGeo_FullName"] = "Localisation inconnue"

    grouped = (
        working.groupby(["ActionGeo_FullName", "ActionGeo_Lat", "ActionGeo_Long"], as_index=False)
        .agg(
            event_count=("AvgTone", "size"),
            avg_tone=("AvgTone", "mean"),
        )
        .rename(
            columns={
                "ActionGeo_FullName": "location",
                "ActionGeo_Lat": "lat",
                "ActionGeo_Long": "lon",
            }
        )
        .sort_values(["event_count", "avg_tone"], ascending=[False, True])
        .reset_index(drop=True)
    )

    if "event_label" in working.columns:
        dominant_events = (
            working.groupby(["ActionGeo_FullName", "ActionGeo_Lat", "ActionGeo_Long"])["event_label"]
            .agg(lambda series: series.value_counts().index[0] if not series.dropna().empty else "N/A")
            .reset_index(name="dominant_event")
            .rename(
                columns={
                    "ActionGeo_FullName": "location",
                    "ActionGeo_Lat": "lat",
                    "ActionGeo_Long": "lon",
                }
            )
        )
        grouped = grouped.merge(dominant_events, on=["location", "lat", "lon"], how="left")
    else:
        grouped["dominant_event"] = "N/A"

    return grouped.head(limit)
