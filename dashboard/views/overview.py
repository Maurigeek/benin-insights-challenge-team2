"""Page Vue d'ensemble — timeline, acteurs, répartition événements."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.ui import render_panel_intro
from src.models.actor_model import extract_actor_counts
from src.models.geo_model import build_geo_event_points

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def _generate_human_insights(monthly: pd.DataFrame, df: pd.DataFrame) -> list:
    """Construit 5 insights sobres, humains et directement appuyés par les données."""

    if monthly.empty or df.empty:
        return []

    total_events = int(len(df))
    pressure_window = monthly[monthly["year_month"].isin(["2026-01", "2026-02", "2026-03", "2026-04"])]
    pressure_share = (pressure_window["count"].sum() / total_events * 100) if not pressure_window.empty else 0.0

    worst_month_row = monthly.loc[monthly["avg_tone"].idxmin()]
    worst_month = worst_month_row["year_month"]
    worst_negative_share = float(worst_month_row.get("negative_share", 0.0) * 100)

    type_share = df["event_label"].value_counts(normalize=True).mul(100)
    top_types = type_share.head(3)
    top_type_text = ", ".join(
        f"<strong>{label}</strong> ({value:.0f}%)" for label, value in top_types.items()
    )

    source_series = (
        df["SOURCEURL"]
        .astype(str)
        .str.extract(r"https?://(?:www\.)?([^/]+)")[0]
        .fillna("inconnu")
    )
    source_counts = source_series.value_counts(normalize=True).mul(100)
    lead_source = source_counts.index[0]
    lead_source_share = float(source_counts.iloc[0])
    top5_source_share = float(source_counts.head(5).sum())

    institutional_types = {"Consultation", "Déclaration publique", "Engagement diplomatique", "Accord / Coopération", "Coopération"}
    security_types = {"Violence de masse", "Coercition", "Protestation", "Désapprobation", "Rejet / Refus"}
    institutional_share = float(df["event_label"].isin(institutional_types).mean() * 100)
    security_share = float(df["event_label"].isin(security_types).mean() * 100)

    location_counts = df["ActionGeo_FullName"].fillna("Inconnu").value_counts()
    local_focus = [
        loc for loc in location_counts.index
        if str(loc).strip().lower() not in {"benin", "inconnu"}
    ][:4]
    local_focus_text = ", ".join(f"<strong>{loc}</strong>" for loc in local_focus) if local_focus else "des foyers secondaires encore diffus"
    north_mask = df["ActionGeo_FullName"].fillna("").str.contains(
        r"Alibori|Kandi|Karimama|Parakou|Borgou|Djougou|Atacora|Atakora|Donga",
        case=False,
        regex=True,
    )
    north_share = float(north_mask.mean() * 100)

    anomalies = []
    if {"is_anomaly", "is_partial_signal"}.issubset(monthly.columns):
        anomalies = monthly.loc[monthly["is_anomaly"], "year_month"].tolist()
    anomaly_text = ", ".join(f"<strong>{month}</strong>" for month in anomalies[:2]) if anomalies else "des mois encore à confirmer"

    insights = [
        (
            "Séquence sous pression",
            f"Le début de 2026 concentre <strong>{pressure_share:.0f}%</strong> du corpus total. La couverture ne grimpe pas sur un seul pic : elle reste élevée plusieurs mois de suite, ce qui signale une séquence de pression durable."
        ),
        (
            "Rupture de ton",
            f"<strong>{worst_month}</strong> est le point de rupture le plus net du corpus : ton moyen à <strong>{worst_month_row['avg_tone']:.2f}</strong> et près de <strong>{worst_negative_share:.0f}%</strong> d'événements négatifs. C'est le moment où le récit devient franchement défavorable."
        ),
        (
            "Politique",
            f"Près de <strong>{institutional_share:.0f}%</strong> du corpus relève de la consultation, de la déclaration publique ou de l'engagement diplomatique. Le Bénin est donc d'abord raconté comme un espace de gestion politique et institutionnelle."
        ),
        (
            "Sécurité",
            f"Les catégories les plus dures — violence, coercition, protestation, désapprobation ou rejet — représentent tout de même <strong>{security_share:.0f}%</strong> du corpus. Le risque sécuritaire n'est pas marginal ; il s'insère dans un récit plus large."
        ),
        (
            "Récit dominant",
            f"Le Bénin est d'abord raconté à travers {top_type_text}. Le signal médiatique est surtout institutionnel et diplomatique, avant d'être purement conflictuel."
        ),
        (
            "Dépendance aux sources",
            f"<strong>{lead_source}</strong> pèse à lui seul <strong>{lead_source_share:.1f}%</strong> du corpus, et les cinq premières sources montent à <strong>{top5_source_share:.1f}%</strong>. Toute lecture du climat médiatique doit donc intégrer un vrai biais de source."
        ),
        (
            "Territoire",
            f"Les foyers qui ressortent le plus hors libellé national sont {local_focus_text}. Le signal visible reste très nationalisé, mais ces points secondaires donnent les premiers ancrages territoriaux vraiment exploitables."
        ),
        (
            "Nord à surveiller",
            f"L'axe nord ne domine pas encore le corpus, mais il représente déjà autour de <strong>{north_share:.1f}%</strong> des localisations nommées. C'est peu en volume, mais suffisant pour justifier une veille distincte."
        ),
        (
            "Points de vigilance",
            f"Côté ruptures, {anomaly_text} méritent une lecture prioritaire, car ce sont les périodes où le signal change vraiment de régime."
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

    render_panel_intro(
        "Insights",
        "Ce qu'il faut retenir sur la période",
        "Lecture synthétique des signaux dominants sur les données filtrées.",
    )

    insights = _generate_human_insights(monthly, df)

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
