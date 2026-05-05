"""KPI cards — métriques clés affichées en haut du dashboard."""

import pandas as pd
import streamlit as st
from components.ui import render_kpi_card


def render_kpis(df: pd.DataFrame, anomaly_monthly: pd.DataFrame | None = None) -> None:
    """Affiche 4 métriques clés en haut de page."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        peak_month = (
            df["year_month"].value_counts().idxmax()
            if "year_month" in df.columns and not df.empty
            else "N/A"
        )
        render_kpi_card("Événements", f"{len(df):,}", f"Pic observé : {peak_month}")

    with col2:
        avg_tone = df["AvgTone"].mean() if not df.empty else 0.0
        pct_neg = (df["AvgTone"] < 0).mean() * 100 if not df.empty else 0.0
        tone = "alert" if avg_tone < 0 else "positive"
        render_kpi_card(
            "Ton médiatique moyen",
            f"{avg_tone:.2f}",
            f"{pct_neg:.0f}% de couverture négative",
            tone=tone,
        )

    with col3:
        if "event_label" in df.columns:
            n_types = df["event_label"].dropna().nunique()
            top_type = (
                df["event_label"].value_counts().index[0]
                if not df["event_label"].dropna().empty else "N/A"
            )
            render_kpi_card(
                "Types d'événements",
                str(n_types),
                f"Dominant : {top_type}",
            )
        else:
            render_kpi_card("Types d'événements", "—", "Aucune catégorie exploitable")

    with col4:
        if anomaly_monthly is not None and "is_anomaly" in anomaly_monthly.columns:
            n_anomalies = int(anomaly_monthly["is_anomaly"].sum())
            top_month = (
                anomaly_monthly.loc[anomaly_monthly["is_anomaly"], "year_month"].iloc[0]
                if n_anomalies > 0 else "Aucune"
            )
            render_kpi_card(
                "Anomalies détectées",
                str(n_anomalies),
                f"Premier signal : {top_month}",
                tone="alert" if n_anomalies > 0 else "neutral",
            )
        else:
            render_kpi_card("Anomalies détectées", "—", "Modèle non disponible")
