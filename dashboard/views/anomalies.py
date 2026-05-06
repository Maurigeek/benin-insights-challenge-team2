"""Page Anomalies — détection Isolation Forest."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.ui import render_panel_intro, render_signal_chip
from src.models.anomaly_model import detect_monthly_anomalies

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def render_anomalies(df: pd.DataFrame, anomaly_monthly: pd.DataFrame | None = None) -> None:
    """Affiche la page Anomalies."""

    if anomaly_monthly is None:
        anomaly_monthly = detect_monthly_anomalies(df).dataframe

    monthly = anomaly_monthly.rename(
        columns={
            "rows": "count",
            "avg_tone": "avg_tone",
            "goldstein_scale": "goldstein",
        }
    ).copy()
    anomalies = monthly[monthly["is_anomaly"]]
    model_method = (
        str(monthly["method"].iloc[0]).replace("_", " ")
        if "method" in monthly.columns and not monthly.empty
        else "inconnu"
    )

    render_panel_intro(
        "Anomalies",
        "Détection des ruptures et pics de tension",
        "Volume, ton et Goldstein pour isoler les périodes hors norme.",
    )

    chip_cols = st.columns(3)
    with chip_cols[0]:
        render_signal_chip("Méthode active", model_method.title())
    with chip_cols[1]:
        render_signal_chip("Périodes signalées", str(len(anomalies)), tone="alert" if not anomalies.empty else "neutral")
    with chip_cols[2]:
        strongest_month = anomalies.iloc[0]["year_month"] if not anomalies.empty else "Aucune"
        render_signal_chip("Premier signal", str(strongest_month))

    left_col, right_col = st.columns([2.2, 1])
    with left_col:
        st.markdown('<div class="bi-plot-frame">', unsafe_allow_html=True)
        render_panel_intro(
            "Signal brut",
            "Volume mensuel et mois anormaux",
            "Les barres rouges correspondent aux mois détectés par le modèle.",
        )
    
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=monthly["year_month"],
            y=monthly["count"],
            marker_color=[
                "#E24B4A" if bool(a) else "#1D9E75"
                for a in monthly["is_anomaly"]
            ],
            name="Volume mensuel",
        ))

        fig.update_layout(
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.10)", title="Événements"),
            showlegend=False,
            font=dict(color="#dbe5f5"),
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        render_panel_intro(
            "Journal d'alerte",
            "Périodes anormales détectées",
            "Résumé rapide des périodes signalées.",
        )
        if anomalies.empty:
            st.info("Aucune anomalie détectée sur la période sélectionnée.")
        else:
            for _, row in anomalies.iterrows():
                st.markdown(
                    f"""
                    <div class="bi-alert-row">
                        <strong>{row['year_month']}</strong><br/>
                        <span>{int(row['count'])} événements · ton {row['avg_tone']:.2f} · Goldstein {row['goldstein']:.2f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if not anomalies.empty:
        render_panel_intro(
            "Détails",
            "Pourquoi ces mois ressortent-ils ?",
            "Événements dominants pour chaque mois signalé.",
        )
        for _, row in anomalies.iterrows():
            with st.expander(f"{row['year_month']} · {int(row['count'])} événements"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Volume", f"{int(row['count'])}")
                col2.metric("Ton moyen", f"{row['avg_tone']:.2f}")
                col3.metric("Goldstein moyen", f"{row['goldstein']:.2f}")

                month_df = df[df["year_month"] == row["year_month"]]
                if "event_label" in month_df.columns:
                    st.caption("Événements dominants :")
                    top_events = month_df["event_label"].value_counts().head(5)
                    st.dataframe(
                        top_events.reset_index().rename(columns={"index": "Événement", "event_label": "Nombre"}),
                        use_container_width=True,
                        hide_index=True,
                    )
