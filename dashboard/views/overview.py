"""Page Vue d'ensemble — timeline, acteurs, répartition événements."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.ui import render_panel_intro
from src.models.actor_model import extract_actor_counts
from src.models.geo_model import build_geo_event_points

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def _generate_human_insights(monthly: pd.DataFrame, df: pd.DataFrame, top_type: str, hottest_month: str,
                           dominant_actor: str, avg_tone: float, anomaly_like_months: list,
                           negative_share: float, goldstein_avg: float, top_source: str,
                           second_type: str, trend_label: str, evidence_note: str) -> list:
    """Génère des insights plus humains et contextuels."""

    # Descriptions de tonalité plus naturelles
    tone_descriptions = {
        "very_negative": "très tendu, comme pendant une crise majeure",
        "negative": "plutôt négatif, avec beaucoup de critiques",
        "mixed": "mitigé, ni vraiment positif ni catastrophique",
        "positive": "globalement positif ou neutre"
    }

    if avg_tone < -2:
        tone_key = "very_negative"
    elif avg_tone < -1:
        tone_key = "negative"
    elif avg_tone < 0:
        tone_key = "mixed"
    else:
        tone_key = "positive"

    tone_description = tone_descriptions[tone_key]

    # Contexte de volume plus parlant
    volume_context = ""
    if len(monthly) > 0 and hottest_month != "N/A":
        avg_volume = monthly["count"].mean()
        hottest_count = monthly.loc[monthly["year_month"] == hottest_month, "count"].iloc[0]
        volume_ratio = hottest_count / avg_volume if avg_volume > 0 else 1

        if volume_ratio > 2.5:
            volume_context = f"avec un emballement médiatique exceptionnel ({volume_ratio:.1f} fois la moyenne normale)"
        elif volume_ratio > 2:
            volume_context = f"avec un pic d'attention inhabituel ({volume_ratio:.1f} fois plus que d'habitude)"
        elif volume_ratio > 1.5:
            volume_context = f"avec une activité {volume_ratio:.1f} fois plus intense que d'habitude"
        else:
            volume_context = "dans une période d'activité plutôt normale"

    # Contexte temporel
    time_context = ""
    if len(monthly) >= 12:
        time_context = "sur cette longue période d'observation"
    elif len(monthly) >= 6:
        time_context = "ces derniers mois"
    else:
        time_context = "dans ce court laps de temps"

    recent_pressure = ", ".join(anomaly_like_months[:2]) if anomaly_like_months else "Aucun pic particulier"

    insights = [
        (
            "📊 Signal principal",
            f"Climat {tone_description}. Focus sur <strong>{top_type.lower()}</strong>, évolution {trend_label} {time_context}. <em>Action : Adapter la stratégie de communication en conséquence.</em>"
        ),
        (
            "Points chauds",
            f"Pic en <strong>{hottest_month}</strong> {volume_context}. Surveillance sur <strong>{recent_pressure}</strong>. <em>Action : Renforcer le monitoring pendant ces périodes critiques.</em>"
        ),
        (
            "Figure centrale",
            f"<strong>{dominant_actor}</strong> domine le discours médiatique avec une présence récurrente."
        ),
        (
            "Climat ambiant",
            f"Négativité à <strong>{negative_share:.0f}%</strong> - niveau élevé nécessitant attention particulière. <em>Action : Préparer une réponse proactive aux critiques.</em>"
        ),
        (
            "⚖️ Niveau de tension",
            f"Goldstein moyen : <strong>{goldstein_avg:.2f}</strong>. Tension générale avec variations ponctuelles."
        ),
        (
            "📡 Porte-voix principal",
            f"<strong>{top_source}</strong> influence significativement le récit général."
        ),
        (
            "Types d'histoires",
            f"Prédominance de <strong>{top_type.lower()}</strong>, suivi de <strong>{second_type.lower()}</strong>. {evidence_note}"
        ),
    ]

    return insights


def render_overview(df: pd.DataFrame) -> None:
    """Affiche la page Vue d'ensemble."""
    monthly = (
        df.groupby("year_month")
        .agg(
            avg_tone=("AvgTone", "mean"),
            goldstein=("GoldsteinScale", "mean"),
            count=("AvgTone", "size"),
        )
        .reset_index()
    )
    top_actors = extract_actor_counts(df, limit=10)
    geo_points = build_geo_event_points(df, limit=120)
    top_type = (
        df["event_label"].value_counts().index[0]
        if "event_label" in df.columns and not df["event_label"].dropna().empty
        else "N/A"
    )
    hottest_month = (
        monthly.loc[monthly["count"].idxmax(), "year_month"]
        if not monthly.empty
        else "N/A"
    )
    dominant_actor = (
        top_actors.iloc[0]["Acteur"]
        if not top_actors.empty
        else "Aucun acteur stable"
    )
    avg_tone = monthly["avg_tone"].mean() if not monthly.empty else 0.0
    anomaly_like_months = monthly.loc[monthly["count"] >= monthly["count"].quantile(0.85), "year_month"].tolist() if not monthly.empty else []
    recent_signal = "Dégradation du climat médiatique" if avg_tone < -1 else "Signal relativement stable"
    recent_pressure = ", ".join(anomaly_like_months[:2]) if anomaly_like_months else "Aucun pic net"
    negative_share = (df["AvgTone"] < 0).mean() * 100 if not df.empty else 0.0
    goldstein_avg = df["GoldsteinScale"].mean() if not df.empty else 0.0
    top_source = (
        df["SOURCEURL"]
        .astype(str)
        .str.extract(r"https?://(?:www\.)?([^/]+)")[0]
        .value_counts()
        .index[0]
        if "SOURCEURL" in df.columns and not df["SOURCEURL"].dropna().empty
        else "Source non identifiée"
    )
    event_mix = (
        df["event_label"].value_counts().head(2).index.tolist()
        if "event_label" in df.columns
        else []
    )
    second_type = event_mix[1] if len(event_mix) > 1 else "Aucun second type net"
    latest_tone = monthly.iloc[-1]["avg_tone"] if not monthly.empty else 0.0
    earliest_tone = monthly.iloc[0]["avg_tone"] if not monthly.empty else 0.0
    tone_delta = latest_tone - earliest_tone
    trend_label = "en amélioration" if tone_delta > 0.2 else "en dégradation" if tone_delta < -0.2 else "relativement stable"
    evidence_note = "Lecture à confirmer avec les prochains mois." if len(monthly) < 18 else "Signal robuste sur une fenêtre temporelle étendue."

    render_panel_intro(
        "Insights",
        "Ce qu'il faut retenir sur la période",
        "Lecture synthétique des signaux dominants sur les données filtrées.",
    )

    insights = _generate_human_insights(
        monthly, df, top_type, hottest_month, dominant_actor, avg_tone,
        anomaly_like_months, negative_share, goldstein_avg, top_source,
        second_type, trend_label, evidence_note
    )

    grouped_insights = [insights[idx:idx + 2] for idx in range(0, len(insights), 2)]
    cards_html = "".join(
        '<div class="bi-insight-column">' +
        "".join(
            f'<div class="bi-card bi-note bi-insight-card">'
            f'<div class="bi-note-title">{title}</div>'
            f'<div class="bi-note-body">{body}</div>'
            f'</div>'
            for title, body in chunk
        ) +
        '</div>'
        for chunk in grouped_insights
    )
    st.markdown(f'<div class="bi-insight-scroll">{cards_html}</div>', unsafe_allow_html=True)

    st.markdown('<div class="bi-plot-frame">', unsafe_allow_html=True)
    render_panel_intro(
        "Tonalité",
        "Évolution du ton médiatique",
        "Ton moyen et Goldstein pour lire les ruptures du signal.",
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
            text="Point critique - Dec 2025",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#E24B4A",
            font=dict(color="#E24B4A", size=11),
        )

    fig_timeline.update_layout(
        height=310,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.10)", title="Indice moyen"),
        font=dict(color="#dbe5f5"),
    )

    st.plotly_chart(fig_timeline, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="bi-plot-frame">', unsafe_allow_html=True)
    render_panel_intro(
        "Territoire",
        "Où les événements se concentrent-ils ?",
        "Carte dynamique basée sur les coordonnées réelles des événements filtrés.",
    )
    if not geo_points.empty:
        geo_points = geo_points.copy()
        geo_points["tone_bucket"] = geo_points["avg_tone"].apply(
            lambda value: "Négatif" if value < -1 else "Sous tension" if value < 0 else "Plutôt positif"
        )
        fig_map = px.scatter_mapbox(
            geo_points,
            lat="lat",
            lon="lon",
            size="event_count",
            color="tone_bucket",
            hover_name="location",
            hover_data={
                "event_count": True,
                "avg_tone": ":.2f",
                "dominant_event": True,
                "lat": False,
                "lon": False,
                "tone_bucket": False,
            },
            color_discrete_map={
                "Négatif": "#E24B4A",
                "Sous tension": "#1D9E75",
                "Plutôt positif": "#378ADD",
            },
            zoom=6.4,
            height=420,
        )
        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#dbe5f5"),
            legend=dict(title="", orientation="h", yanchor="bottom", y=1.02),
        )
        fig_map.update_traces(marker=dict(opacity=0.8))
        st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("Aucune coordonnée exploitable sur la période sélectionnée.")
    st.markdown("</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="bi-plot-frame">', unsafe_allow_html=True)
        render_panel_intro(
            "Acteurs",
            "Qui structure la narration ?",
            "Acteurs recalculés dynamiquement à partir des données filtrées.",
        )
        if not top_actors.empty:
            fig_actors = px.bar(
                top_actors,
                x="Nombre",
                y="Acteur",
                orientation="h",
                color_discrete_sequence=["#1D9E75"],
            )
            fig_actors.update_layout(
                height=335,
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.10)", title="Occurrences"),
                yaxis_title="",
                font=dict(color="#dbe5f5"),
            )
            st.plotly_chart(fig_actors, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Aucun acteur exploitable apres nettoyage.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="bi-plot-frame">', unsafe_allow_html=True)
        render_panel_intro(
            "Structure",
            "Répartition des événements",
            "Familles d'événements qui concentrent la couverture.",
        )
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
                height=335,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(font=dict(size=10)),
                font=dict(color="#dbe5f5"),
            )
            fig_events.update_traces(textposition="inside", textfont_size=10)
            st.plotly_chart(fig_events, use_container_width=True, config=PLOTLY_CONFIG)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="bi-plot-frame">', unsafe_allow_html=True)
    render_panel_intro(
        "Cadence",
        "Volume mensuel d'événements",
        "Intensité de couverture sur la période.",
    )
    monthly_vol = df.groupby("year_month").size().reset_index(name="count")

    fig_vol = px.bar(
        monthly_vol,
        x="year_month",
        y="count",
        color_discrete_sequence=["#378ADD"],
    )
    fig_vol.update_layout(
        height=260,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.10)", title="Nombre d'événements"),
        font=dict(color="#dbe5f5"),
    )
    st.plotly_chart(fig_vol, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)
