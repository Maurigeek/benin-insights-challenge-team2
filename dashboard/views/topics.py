"""Page Topics — visualisation BERTopic."""

import pandas as pd
import plotly.express as px
import streamlit as st


def render_topics(df: pd.DataFrame) -> None:
    """Affiche la page Topics."""

    if "topic" not in df.columns:
        st.warning("Les topics ne sont pas encore calculés.")
        return

    st.markdown("#### Répartition des topics détectés")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        topic_counts = (
            df["topic"]
            .dropna()
            .value_counts()
            .reset_index()
        )
        topic_counts.columns = ["Topic", "Nombre"]

        fig = px.bar(
            topic_counts,
            x="Nombre",
            y="Topic",
            orientation="h",
            color="Nombre",
            color_continuous_scale="Teal",
        )
        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Évolution des topics dans le temps")
        if "year_month" in df.columns:
            topic_time = (
                df.groupby(["year_month", "topic"])
                .size()
                .reset_index(name="count")
            )
            fig2 = px.area(
                topic_time,
                x="year_month",
                y="count",
                color="topic",
                color_discrete_sequence=px.colors.sequential.Teal,
            )
            fig2.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(title=""),
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Exemples par topic")
    selected_topic = st.selectbox(
        "Choisir un topic",
        options=df["topic"].dropna().unique().tolist(),
    )
    sample = df[df["topic"] == selected_topic][["date", "event_label", "AvgTone", "GoldsteinScale"]].head(10)
    st.dataframe(sample, use_container_width=True, hide_index=True)
