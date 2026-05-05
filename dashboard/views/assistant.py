"""Page Assistant IA — chat Gemini sur les données GDELT Bénin."""

import json
import pandas as pd
import streamlit as st

from src.models.anomaly_model import detect_monthly_anomalies


def render_assistant(df: pd.DataFrame) -> None:
    """Affiche la page Assistant IA."""

    st.markdown("#### Assistant IA — Posez vos questions sur le Bénin")
    st.caption("L'assistant répond uniquement à partir des données GDELT. Les incertitudes sont explicitement signalées.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ex : Que s'est-il passé au Bénin en décembre 2025 ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                response = query_gemini(prompt, df)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.session_state.messages:
        if st.button("Effacer la conversation"):
            st.session_state.messages = []
            st.rerun()


def build_context(df: pd.DataFrame) -> str:
    """Construit le contexte GDELT à injecter dans le prompt."""
    monthly = (
        df.groupby("year_month")
        .agg(count=("AvgTone", "size"), avg_tone=("AvgTone", "mean"))
        .reset_index()
        .tail(16)
    )

    top_events = df["event_label"].value_counts().head(5).to_dict() if "event_label" in df.columns else {}
    anomaly_monthly = detect_monthly_anomalies(df).dataframe if not df.empty else pd.DataFrame()
    anomaly_months = (
        anomaly_monthly.loc[anomaly_monthly["is_anomaly"], "year_month"].tolist()
        if not anomaly_monthly.empty and "is_anomaly" in anomaly_monthly.columns
        else []
    )
    n_anomalies = len(anomaly_months)

    context = f"""
Données GDELT Bénin disponibles :
- Période : {df['date_parsed'].min().date()} → {df['date_parsed'].max().date()}
- Nombre d'événements : {len(df):,}
- Ton médiatique moyen : {df['AvgTone'].mean():.2f}
- Goldstein Scale moyen : {df['GoldsteinScale'].mean():.2f}
- Couverture négative : {(df['AvgTone'] < 0).mean()*100:.0f}%
- Anomalies détectées : {n_anomalies}
- Mois anormaux : {", ".join(anomaly_months) if anomaly_months else "aucun signal net"}
- Événements dominants : {json.dumps(top_events, ensure_ascii=False)}
- Volume mensuel (derniers mois) :
{monthly.to_string(index=False)}

Biais à signaler : sources majoritairement nigérianes (punchng, dailypost), biais anglophones.
"""
    return context


def query_gemini(prompt: str, df: pd.DataFrame) -> str:
    """Envoie la question à Gemini avec le contexte GDELT."""
    try:
        import google.generativeai as genai
        import os

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return _fallback_response(prompt, df)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        system_prompt = f"""Tu es un assistant d'analyse des données GDELT pour le Bénin.
Tu réponds uniquement à partir des données GDELT fournies.
Tu signales explicitement les incertitudes et les biais de couverture.
Tu n'inventes pas de faits. Si les données sont insuffisantes, tu le dis clairement.

{build_context(df)}
"""
        history = [
            {"role": m["role"], "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]

        chat = model.start_chat(history=history)
        response = chat.send_message(system_prompt + "\n\nQuestion : " + prompt)
        return response.text

    except Exception:
        return _fallback_response(prompt, df)


def _fallback_response(prompt: str, df: pd.DataFrame) -> str:
    """Réponse de fallback si Gemini n'est pas disponible."""
    n = len(df)
    avg = df["AvgTone"].mean()
    return (
        f"**Réponse basée sur les données GDELT** :\n\n"
        f"Sur {n:,} événements analysés, le ton médiatique moyen est de **{avg:.2f}**. "
        f"{'La couverture est majoritairement négative.' if avg < 0 else 'La couverture est globalement positive.'}"
    )
