"""
Bénin Insights Dashboard
Intelligence Médiatique — GDELT 2025-2026
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT))
sys.path.append(str(APP_DIR))

from components.filters import render_sidebar
from components.kpi_cards import render_kpis
from views.anomalies import render_anomalies
from views.assistant import render_assistant
from views.overview import render_overview
from src.models.anomaly import detect_monthly_anomalies

st.set_page_config(
	page_title="Bénin Insights",
	page_icon="🇧🇯",
	layout="wide",
	initial_sidebar_state="expanded",
)

st.markdown(
	"""
<style>
	:root {
		--surface: rgba(14, 22, 38, 0.94);
		--surface-soft: rgba(18, 27, 45, 0.86);
		--border: rgba(148, 163, 184, 0.14);
		--border-strong: rgba(148, 163, 184, 0.22);
		--text: #eef4ff;
		--muted: #8ea0bc;
		--green-soft: rgba(31, 181, 143, 0.10);
		--red-soft: rgba(255, 107, 107, 0.10);
		--blue-soft: rgba(96, 165, 250, 0.10);
	}
	html, body, [class*="css"]  {
		font-family: "Avenir Next", "Segoe UI Variable", "Source Sans Pro", sans-serif;
	}
	[data-testid="stHeader"],
	[data-testid="stToolbar"],
	[data-testid="stDecoration"],
	#MainMenu,
	header {
		display: none !important;
	}
	[data-testid="stSidebarNav"] { display: none; }
	.block-container {
		padding-top: 0.65rem;
		padding-bottom: 1.4rem;
		max-width: 1200px;
	}
	.stApp {
		margin-top: 0;
		background:
			radial-gradient(circle at top left, rgba(96, 165, 250, 0.08), transparent 24%),
			linear-gradient(180deg, #08111e 0%, #0b1220 60%, #0d1423 100%);
		color: var(--text);
	}
	[data-testid="stSidebar"] {
		min-width: 260px;
		max-width: 280px;
		background: rgba(245, 247, 251, 0.98);
		border-right: 1px solid var(--border);
	}
	[data-testid="stSidebar"] > div:first-child {
		padding-top: 0 !important;
	}
	[data-testid="stSidebar"] > div,
	[data-testid="stSidebarContent"] {
		background: rgba(245, 247, 251, 0.98);
	}
	[data-testid="stSidebarContent"] {
		padding-top: 0 !important;
	}
	[data-testid="stSidebar"] * { color: #111111; }
	[data-testid="stSidebar"] .stCaption { color: #4b5563; }
	[data-testid="stSidebar"] label { color: #111111; }
	[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
	[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
	[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
		color: #1f2937 !important;
	}
	[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
		color: #0f172a !important;
	}
	[data-testid="stSidebar"] [data-baseweb="select"] > div,
	[data-testid="stSidebar"] [data-baseweb="input"] > div {
		background: #ffffff;
		border: 1px solid var(--border);
		color: #111111;
		box-shadow: none;
	}
	[data-testid="stSidebar"] [data-baseweb="select"] svg {
		color: #111111;
	}
	[data-testid="stSidebar"] input,
	[data-testid="stSidebar"] select,
	[data-testid="stSidebar"] textarea {
		color: #111111 !important;
	}
	section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
	button[kind="header"] {
		top: 0.35rem !important;
	}
	[data-testid="stSidebar"] h3 { font-weight: 600; letter-spacing: 0.2px; }
	[data-testid="stSidebar"] hr { margin: 0.65rem 0; border-color: rgba(15, 23, 42, 0.08); }
	[data-testid="stSidebar"] .stDateInput label,
	[data-testid="stSidebar"] .stSelectbox label,
	[data-testid="stSidebar"] .stCheckbox label {
		color: #374151 !important;
		font-weight: 600;
	}
	[data-testid="stMarkdownContainer"] p { color: var(--text); }
	.bi-hero {
		padding: 1.2rem 1.3rem;
		border: 1px solid var(--border);
		border-radius: 20px;
		background: linear-gradient(180deg, rgba(16, 25, 42, 0.96), rgba(12, 19, 34, 0.96));
	}
	.bi-eyebrow {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.35rem 0.7rem;
		border-radius: 999px;
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid var(--border);
		font-size: 0.75rem;
		color: #d7e0ef;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	.bi-hero h1 {
		margin: 0.7rem 0 0.2rem;
		font-size: 2rem;
		line-height: 1.05;
		letter-spacing: -0.03em;
		color: #f8fbff;
	}
	.bi-hero p {
		margin: 0;
		color: var(--muted);
		font-size: 0.98rem;
		max-width: 48rem;
	}
	.bi-nav {
		padding: 0;
		background: transparent;
	}
	.bi-nav .stButton > button {
		height: 2.8rem;
		border-radius: 12px;
		border: 1px solid var(--border);
		background: rgba(255, 255, 255, 0.02);
		color: #dbe5f5;
		font-weight: 600;
		letter-spacing: 0.01em;
	}
	.bi-nav .stButton > button:hover {
		border-color: var(--border-strong);
		background: rgba(255, 255, 255, 0.05);
		color: #ffffff;
	}
	.bi-nav .stButton > button[kind="primary"] {
		background: rgba(96, 165, 250, 0.12);
		border-color: rgba(96, 165, 250, 0.28);
		color: #ffffff;
	}
	.bi-card {
		border: 1px solid var(--border);
		border-radius: 18px;
		background: linear-gradient(180deg, rgba(16, 24, 42, 0.94), rgba(12, 19, 34, 0.98));
	}
	.bi-kpi {
		padding: 1rem 1rem 0.9rem;
		min-height: 132px;
	}
	.bi-kpi-label {
		color: var(--muted);
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	.bi-kpi-value {
		margin-top: 0.5rem;
		color: #ffffff;
		font-size: 2rem;
		font-weight: 700;
		letter-spacing: -0.04em;
	}
	.bi-kpi-meta {
		margin-top: 0.75rem;
		display: inline-flex;
		align-items: center;
		padding: 0.35rem 0.7rem;
		border-radius: 999px;
		font-size: 0.8rem;
	}
	.bi-kpi-positive .bi-kpi-meta {
		background: var(--green-soft);
		color: #7be2c4;
	}
	.bi-kpi-alert .bi-kpi-meta {
		background: var(--red-soft);
		color: #ff9d9d;
	}
	.bi-kpi-neutral .bi-kpi-meta {
		background: rgba(255, 255, 255, 0.06);
		color: #dbe5f5;
	}
	.bi-note {
		padding: 1rem 1rem 0.95rem;
		min-height: 128px;
	}
	.bi-note-title {
		color: #f6fbff;
		font-size: 0.95rem;
		font-weight: 600;
	}
	.bi-note-body {
		margin-top: 0.45rem;
		color: var(--muted);
		font-size: 0.92rem;
		line-height: 1.55;
	}
	.bi-note-body strong {
		color: #ffffff;
		font-weight: 600;
	}
	.bi-insight-scroll {
		display: flex;
		gap: 0.9rem;
		overflow-x: auto;
		padding: 0.2rem 0 0.55rem;
		margin-top: 1.35rem;
		margin-bottom: 1.75rem;
		scroll-snap-type: x proximity;
		scrollbar-width: thin;
	}
	.bi-insight-scroll::-webkit-scrollbar {
		height: 8px;
	}
	.bi-insight-scroll::-webkit-scrollbar-thumb {
		background: rgba(148, 163, 184, 0.35);
		border-radius: 999px;
	}
	.bi-insight-column {
		flex: 0 0 320px;
		scroll-snap-align: start;
		display: flex;
		flex-direction: column;
		gap: 0.9rem;
	}
	.bi-insight-card {
		width: 100%;
	}
	.bi-panel-intro {
		margin-top: 1.35rem;
		margin-bottom: 0.7rem;
	}
	.bi-kicker {
		color: #7be2c4;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}
	.bi-section-title {
		margin-top: 0.18rem;
		font-size: 1.35rem;
		font-weight: 700;
		letter-spacing: -0.03em;
		color: #f8fbff;
	}
	.bi-section-subtitle {
		margin-top: 0.3rem;
		color: var(--muted);
		font-size: 0.9rem;
		max-width: 48rem;
	}
	.bi-plot-frame {
		padding: 0.95rem 0.95rem 0.25rem;
		border: 1px solid var(--border);
		border-radius: 18px;
		background: rgba(13, 20, 35, 0.82);
		margin-top: 1.45rem;
		margin-bottom: 1.2rem;
	}
	.bi-alert-row {
		padding: 0.95rem 1rem;
		border-radius: 18px;
		border: 1px solid var(--border);
		background: rgba(255, 255, 255, 0.03);
		margin-bottom: 0.75rem;
	}
	.bi-alert-row strong { color: #ffffff; }
	.bi-alert-row span { color: var(--muted); }
	[data-testid="stExpander"] {
		border: 1px solid var(--border) !important;
		border-radius: 16px !important;
		background: rgba(255, 255, 255, 0.03);
	}
</style>
""",
	unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Chargement des données...")
def load_data() -> pd.DataFrame:
	path = ROOT / "data" / "processed" / "gdelt_benin_clean.csv"
	df = pd.read_csv(path)
	df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
	df["year_month"] = df["date_parsed"].dt.to_period("M").astype(str)
	return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
	"""Applique les filtres sidebar au DataFrame principal."""
	mask = pd.Series(True, index=df.index)

	start, end = filters["periode"]
	mask &= df["date_parsed"].dt.date >= start
	mask &= df["date_parsed"].dt.date <= end

	if filters.get("theme") and filters["theme"] != "Tous":
		mask &= df["event_label"].astype(str).str.contains(
			filters["theme"], case=False, na=False
		)

	filtered = df.loc[mask].copy()

	if filters.get("anomalies_only") and not filtered.empty:
		anomaly_monthly = detect_monthly_anomalies(filtered).dataframe
		anomaly_months = anomaly_monthly.loc[anomaly_monthly["is_anomaly"], "year_month"].tolist()
		filtered = filtered[filtered["year_month"].isin(anomaly_months)].copy()

	return filtered


def main() -> None:
	df = load_data()

	filters = render_sidebar(df)
	df_filtered = apply_filters(df, filters)
	anomaly_monthly = detect_monthly_anomalies(df_filtered).dataframe
	n_anomalies = int(anomaly_monthly["is_anomaly"].sum()) if "is_anomaly" in anomaly_monthly else 0
	top_type = (
		df_filtered["event_label"].value_counts().index[0]
		if "event_label" in df_filtered.columns and not df_filtered["event_label"].dropna().empty
		else "N/A"
	)
	avg_tone = df_filtered["AvgTone"].mean() if not df_filtered.empty else 0.0
	tone_status = "Tension élevée" if avg_tone < -1.5 else "Sous surveillance" if avg_tone < 0 else "Climat apaisé"

	st.markdown(
		f"""
		<div class="bi-hero">
			<div class="bi-eyebrow">🇧🇯 Tableau de veille Bénin</div>
			<h1>Bénin Insights</h1>
			<p>{len(df_filtered):,} événements analysés du {filters['periode'][0]} au {filters['periode'][1]}.</p>
		</div>
		""",
		unsafe_allow_html=True,
	)

	col_nav = st.columns([1])[0]
	with col_nav:
		if "active_page" not in st.session_state:
			st.session_state.active_page = "Vue d'ensemble"

		labels = ["Vue d'ensemble", "Anomalies", "Assistant IA"]
		st.markdown('<div class="bi-nav">', unsafe_allow_html=True)
		cols = st.columns(len(labels))
		for idx, label in enumerate(labels):
			button_type = "primary" if st.session_state.active_page == label else "secondary"
			if cols[idx].button(label, use_container_width=True, type=button_type):
				st.session_state.active_page = label
		st.markdown("</div>", unsafe_allow_html=True)

		page = st.session_state.active_page

	render_kpis(df_filtered, anomaly_monthly=anomaly_monthly)

	if page == "Vue d'ensemble":
		render_overview(df_filtered)
	elif page == "Anomalies":
		render_anomalies(df_filtered, anomaly_monthly=anomaly_monthly)
	elif page == "Assistant IA":
		render_assistant(df_filtered)


if __name__ == "__main__":
	main()
