"""KPI cards — métriques clés affichées en haut du dashboard."""

import pandas as pd
import streamlit as st


def render_kpis(df: pd.DataFrame) -> None:
    """Affiche 4 métriques clés en haut de page."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Événements",
            value=f"{len(df):,}",
            delta=None,
        )

    with col2:
        avg_tone = df["AvgTone"].mean()
        pct_neg = (df["AvgTone"] < 0).mean() * 100
        st.metric(
            label="Ton médiatique moyen",
            value=f"{avg_tone:.2f}",
            delta=f"{pct_neg:.0f}% négatif",
            delta_color="inverse",
        )

    with col3:
        if "topic" in df.columns:
            n_topics = df["topic"].dropna().nunique()
            top_topic = (
                df["topic"].value_counts().index[0]
                if not df["topic"].dropna().empty else "N/A"
            )
            st.metric(
                label="Topics détectés",
                value=str(n_topics),
                delta=f"Dominant : {top_topic}",
                delta_color="off",
            )
        else:
            st.metric(label="Topics détectés", value="—")

    with col4:
        if "is_anomaly" in df.columns:
            n_anomalies = (df["is_anomaly"] == -1).sum()
            st.metric(
                label="Anomalies détectées",
                value=str(n_anomalies),
                delta="Déc 2025" if n_anomalies > 0 else "Aucune",
                delta_color="inverse" if n_anomalies > 0 else "off",
            )
        else:
            st.metric(label="Anomalies", value="—")
