"""UI helpers for dashboard presentation."""

import streamlit as st


def render_kpi_card(label: str, value: str, meta: str = "", tone: str = "neutral") -> None:
    """Render a styled KPI card with optional meta text."""
    st.markdown(
        f"""
        <div class="bi-card bi-kpi bi-kpi-{tone}">
            <div class="bi-kpi-label">{label}</div>
            <div class="bi-kpi-value">{value}</div>
            <div class="bi-kpi-meta">{meta or "&nbsp;"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_intro(kicker: str, title: str, subtitle: str = "") -> None:
    """Render a small section heading block."""
    st.markdown(
        f"""
        <div class="bi-panel-intro">
            <div class="bi-kicker">{kicker}</div>
            <div class="bi-section-title">{title}</div>
            <div class="bi-section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_signal_chip(label: str, value: str, tone: str = "neutral") -> None:
    """Render a compact signal chip."""
    st.markdown(
        f"""
        <div class="bi-chip bi-chip-{tone}">
            <span class="bi-chip-label">{label}</span>
            <span class="bi-chip-value">{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_note_card(title: str, body: str, tone: str = "neutral") -> None:
    """Render a compact explanatory card."""
    st.markdown(
        f"""
        <div class="bi-card bi-note bi-note-{tone}">
            <div class="bi-note-title">{title}</div>
            <div class="bi-note-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
