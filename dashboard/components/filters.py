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

        st.divider()

        themes = ["Tous"] + sorted(
            df["event_label"].dropna().unique().tolist()
        )
        theme = st.selectbox("Type d'événement", options=themes)

        st.divider()

        anomalies_only = False
        if "is_anomaly" in df.columns:
            anomalies_only = st.checkbox("Anomalies uniquement")

        st.divider()

        st.markdown("**Signal actuel**")
        avg_tone = df["AvgTone"].mean()
        goldstein = df["GoldsteinScale"].mean()
        pct_neg = (df["AvgTone"] < 0).mean() * 100

        tone_label = "Negatif" if avg_tone < -2 else "Mitige" if avg_tone < 0 else "Positif"
        st.caption(f"Ton moyen : **{avg_tone:.2f}** · {tone_label}")
        st.caption(f"Goldstein : **{goldstein:.2f}**")
        st.caption(f"Couverture negative : **{pct_neg:.0f}%**")

        st.divider()

        st.markdown("**Biais GDELT**")
        top_source = (
            df["SOURCEURL"]
            .str.extract(r"https?://(?:www\.)?([^/]+)")[0]
            .value_counts()
            .index[0]
            if "SOURCEURL" in df.columns else "N/A"
        )
        st.caption(f"Source dominante : `{top_source}`")
        st.caption("Biais anglophones/nigerians")
        st.caption("Lacune : juin 2025")

    return {
        "periode": periode,
        "theme": theme,
        "anomalies_only": anomalies_only,
    }
