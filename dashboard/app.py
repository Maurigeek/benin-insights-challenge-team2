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
from views.topics import render_topics

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
		--surface: #ffffff;
		--border: rgba(0, 0, 0, 0.08);
		--muted: rgba(0, 0, 0, 0.6);
	}
	[data-testid="stHeader"],
	[data-testid="stToolbar"],
	[data-testid="stDecoration"],
	#MainMenu,
	header {
		display: none !important;
	}
	[data-testid="stSidebarNav"] { display: none; }
	.block-container { padding-top: 0.4rem; padding-bottom: 1rem; }
	.stApp { margin-top: 0; }
	[data-testid="stSidebar"] {
		min-width: 260px;
		max-width: 280px;
		background: var(--surface);
		border-right: 1px solid var(--border);
	}
	[data-testid="stSidebar"] > div,
	[data-testid="stSidebarContent"] {
		background: var(--surface);
	}
	[data-testid="stSidebar"] * { color: #111111; }
	[data-testid="stSidebar"] .stCaption { color: #444444; }
	[data-testid="stSidebar"] label { color: #111111; }
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
	section[data-testid="stSidebar"] > div:first-child { padding-top: 0.75rem; }
	[data-testid="stSidebar"] h3 { font-weight: 600; letter-spacing: 0.2px; }
	[data-testid="stSidebar"] hr { margin: 0.75rem 0; border-color: var(--border); }
	.stMetric label { font-size: 12px; color: #cfd3d8; }
	.stMetric [data-testid="stMetricValue"] { color: #f2f4f8; }
	.stMetric [data-testid="stMetricDelta"] { color: #ff7b7b; }
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

	if filters.get("anomalies_only") and "is_anomaly" in df.columns:
		mask &= df["is_anomaly"] == -1

	return df.loc[mask].copy()


def main() -> None:
	df = load_data()

	filters = render_sidebar(df)
	df_filtered = apply_filters(df, filters)

	col_title, col_nav = st.columns([3, 5])
	with col_title:
		st.markdown("### 🇧🇯 Bénin Insights")
		st.caption(f"{len(df_filtered):,} événements · {filters['periode'][0]} → {filters['periode'][1]}")

	with col_nav:
		if "active_page" not in st.session_state:
			st.session_state.active_page = "Vue d'ensemble"

		labels = ["Vue d'ensemble", "Topics", "Anomalies", "Assistant IA"]
		cols = st.columns(len(labels))
		for idx, label in enumerate(labels):
			if cols[idx].button(label, use_container_width=True):
				st.session_state.active_page = label

		page = st.session_state.active_page

	st.divider()
	render_kpis(df_filtered)
	st.divider()

	if page == "Vue d'ensemble":
		render_overview(df_filtered)
	elif page == "Topics":
		render_topics(df_filtered)
	elif page == "Anomalies":
		render_anomalies(df_filtered)
	elif page == "Assistant IA":
		render_assistant(df_filtered)


if __name__ == "__main__":
	main()
