"""Page Vue d'ensemble — timeline, acteurs, répartition événements."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_overview(df: pd.DataFrame) -> None:
    """Affiche la page Vue d'ensemble."""

    st.markdown("#### Évolution du ton médiatique")

    monthly = (
        df.groupby("year_month")
        .agg(
            avg_tone=("AvgTone", "mean"),
            goldstein=("GoldsteinScale", "mean"),
            count=("AvgTone", "size"),
        )
        .reset_index()
    )

    fig_timeline = go.Figure()

    fig_timeline.add_trace(go.Scatter(
        x=monthly["year_month"],
        y=monthly["avg_tone"],
        mode="lines+markers",
        name="Ton moyen",
        line=dict(color="#1D9E75", width=2),
        marker=dict(size=4),
    ))

    fig_timeline.add_trace(go.Scatter(
        x=monthly["year_month"],
        y=monthly["goldstein"],
        mode="lines",
        name="Goldstein Scale",
        line=dict(color="#378ADD", width=1.5, dash="dot"),
    ))

    fig_timeline.add_hline(y=0, line_width=0.5, line_dash="dash", line_color="gray")

    if "2025-12" in monthly["year_month"].values:
        dec_row = monthly[monthly["year_month"] == "2025-12"].iloc[0]
        fig_timeline.add_annotation(
            x="2025-12",
            y=dec_row["avg_tone"],
            text="⚠️ Déc 2025",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#E24B4A",
            font=dict(color="#E24B4A", size=11),
        )

    fig_timeline.update_layout(
        height=260,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)"),
    )

    st.plotly_chart(fig_timeline, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Top acteurs")
        if "Actor1Name" in df.columns:
            top_actors = (
                df["Actor1Name"]
                .value_counts()
                .head(10)
                .reset_index()
            )
            top_actors.columns = ["Acteur", "Nombre"]
            top_actors = top_actors[top_actors["Acteur"] != ""]

            fig_actors = px.bar(
                top_actors,
                x="Nombre",
                y="Acteur",
                orientation="h",
                color_discrete_sequence=["#1D9E75"],
            )
            fig_actors.update_layout(
                height=280,
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)"),
            )
            st.plotly_chart(fig_actors, use_container_width=True)

    with col_right:
        st.markdown("#### Répartition des événements")
        if "event_label" in df.columns:
            event_counts = (
                df["event_label"]
                .value_counts()
                .head(8)
                .reset_index()
            )
            event_counts.columns = ["Événement", "Nombre"]

            fig_events = px.pie(
                event_counts,
                names="Événement",
                values="Nombre",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Teal,
            )
            fig_events.update_layout(
                height=280,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(font=dict(size=10)),
            )
            fig_events.update_traces(textposition="inside", textfont_size=10)
            st.plotly_chart(fig_events, use_container_width=True)

    st.markdown("#### Volume mensuel d'événements")
    monthly_vol = df.groupby("year_month").size().reset_index(name="count")

    fig_vol = px.bar(
        monthly_vol,
        x="year_month",
        y="count",
        color_discrete_sequence=["#378ADD"],
    )
    fig_vol.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.1)", title=""),
    )
    st.plotly_chart(fig_vol, use_container_width=True)
