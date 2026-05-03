"""Page Anomalies — détection Isolation Forest."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_anomalies(df: pd.DataFrame) -> None:
    """Affiche la page Anomalies."""

    st.markdown("#### Détection d'anomalies — Signal GDELT Bénin")

    monthly = (
        df.groupby("year_month")
        .agg(
            avg_tone=("AvgTone", "mean"),
            goldstein=("GoldsteinScale", "mean"),
            count=("AvgTone", "size"),
        )
        .reset_index()
    )

    if "is_anomaly" not in df.columns:
        threshold = monthly["count"].mean() + monthly["count"].std()
        monthly["is_anomaly"] = monthly["count"].apply(
            lambda x: -1 if x > threshold else 1
        )
    else:
        monthly_anomaly = (
            df.groupby("year_month")["is_anomaly"]
            .apply(lambda x: -1 if (x == -1).any() else 1)
            .reset_index()
        )
        monthly = monthly.merge(monthly_anomaly, on="year_month", how="left")

    anomalies = monthly[monthly["is_anomaly"] == -1]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly["year_month"],
        y=monthly["count"],
        marker_color=[
            "#E24B4A" if a == -1 else "#1D9E75"
            for a in monthly["is_anomaly"]
        ],
        name="Volume mensuel",
    ))

    threshold = monthly["count"].mean() + monthly["count"].std()
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="#EF9F27",
        annotation_text=f"Seuil anomalie ({threshold:.0f})",
        annotation_position="top right",
        annotation_font=dict(color="#EF9F27", size=11),
    )

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)", title="Événements"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Périodes anormales détectées")

    if anomalies.empty:
        st.info("Aucune anomalie détectée sur la période sélectionnée.")
    else:
        for _, row in anomalies.iterrows():
            with st.expander(f"⚠️ {row['year_month']} — {int(row['count'])} événements"):
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
