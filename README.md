# Bénin Insights Challenge — Team 2
> Analyse des données GDELT sur le Bénin (jan 2025 – avr 2026)
> iSHEERO × DataCamp Donates | Hackathon 2026

---

## Équipe

| Rôle            | Nom et Prénoms                         |
|-----------------|----------------------------------------|
| Data Engineer   | MEDEHO TOTTIN Maurias                  |
| Data Analyst    | AGBOTON Immaculée Irmine Noellie Sènami|
| ML Engineer     | ADANDE Appolinaire                     |
| Data Scientist  | AKO Hillary                            |
---

## Stack

`Python` `BigQuery` `Pandas` `Streamlit` `Plotly` `Scikit-learn` `HuggingFace`

---

## Structure

```
├── data/
│   ├── raw/                    # Données brutes BigQuery
│   └── processed/              # Données nettoyées et agrégées
├── pipeline/
│   ├── config.py               # Paramètres centralisés
│   ├── extract.py              # Extraction BigQuery
│   ├── transform.py            # Nettoyage
│   ├── load.py                 # Export
│   └── queries.sql             # Requêtes documentées
├── notebooks/                  # Analyses exploratoires
├── models/                     # Entraînement et évaluation ML
├── dashboard/                  # Application Streamlit
├── reports/                    # Insights et résumé exécutif
├── Makefile
└── requirements.txt
```

---

## Démarrage rapide

> Les données sont déjà dans `data/` — pas besoin de relancer BigQuery.

**Mac / Linux**
```bash
git clone https://github.com/Maurigeek/benin-insights-challenge-team2
cd benin-insights-challenge-team2
make install      # crée le venv + installe les dépendances
make all          # lance toute la pipeline
make dashboard    # lance le dashboard
```

**Windows**
```bash
git clone https://github.com/Maurigeek/benin-insights-challenge-team2
cd benin-insights-challenge-team2
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python pipeline/extract.py
python pipeline/transform.py
python pipeline/load.py
streamlit run dashboard/app.py
```

---

## Usage de l'IA

Ce projet utilise Claude (Anthropic) pour orienter l'exploration des données
et structurer l'architecture. Tout le code et les analyses sont produits
et validés par l'équipe.