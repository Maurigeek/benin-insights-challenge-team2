"""Sidebar — filtres globaux du dashboard."""

import pandas as pd
import streamlit as st


def render_sidebar(df: pd.DataFrame) -> dict:
    """
    Affiche les filtres dans la sidebar.
    Retourne un dict avec les valeurs sélectionnées.
    """
    with st.sidebar:
        st.markdown("### Filtres")

        min_date = df["date_parsed"].min().date()
        max_date = df["date_parsed"].max().date()

        periode = st.date_input(
            "Période",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if len(periode) != 2:
            periode = (min_date, max_date)

        themes = ["Tous"] + sorted(
            df["event_label"].dropna().unique().tolist()
        )
        theme = st.selectbox("Type d'événement", options=themes)

        st.divider()
        anomalies_only = st.checkbox("Anomalies uniquement")

        avg_tone = df["AvgTone"].mean()
        goldstein = df["GoldsteinScale"].mean()
        pct_neg = (df["AvgTone"] < 0).mean() * 100
        tone_label = "Négatif" if avg_tone < -2 else "Mitigé" if avg_tone < 0 else "Positif"
        top_type = (
            df["event_label"].value_counts().index[0]
            if "event_label" in df.columns and not df["event_label"].dropna().empty
            else "N/A"
        )

        st.divider()

        st.markdown("**Repères utiles**")
        st.caption(f"Ton moyen : **{avg_tone:.2f}** ({tone_label})")
        st.caption(f"Couverture négative : **{pct_neg:.0f}%**")
        st.caption(f"Type dominant : **{top_type}**")
        st.caption(f"Goldstein moyen : **{goldstein:.2f}**")

        st.divider()

        st.markdown("**Source dominante**")
        top_source = (
            df["SOURCEURL"]
            .str.extract(r"https?://(?:www\.)?([^/]+)")[0]
            .value_counts()
            .index[0]
            if "SOURCEURL" in df.columns else "N/A"
        )
        st.caption(f"`{top_source}`")

    return {
        "periode": periode,
        "theme": theme,
        "anomalies_only": anomalies_only,
    }
