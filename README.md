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

```bash
git clone https://github.com/isheero-org/benin-insights-challenge-team2
cd benin-insights-challenge-team2
pip install -r requirements.txt
make all          # Lance toute la pipeline
make dashboard    # Lance le dashboard
```

> ⚠️ Les données sont déjà dans `data/` — pas besoin de relancer BigQuery.
> Chaque membre utilise son propre compte Google Cloud si nécessaire (1 TB gratuit/mois).

---

## Usage de l'IA

Ce projet utilise Claude (Anthropic) pour orienter l'exploration des données
et structurer l'architecture. Tout le code et les analyses sont produits
et validés par l'équipe.