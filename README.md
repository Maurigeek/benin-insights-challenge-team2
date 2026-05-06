# 🇧🇯 Bénin Insights — GDELT Analytics & Dashboard (Team 2)
> Analyse des données GDELT sur le Bénin (jan 2025 – avr 2026)
> iSHEERO × DataCamp Donates | Hackathon 2026

---

## Demo

![Demo dashboard](demo.png)

Lien demo : http://benin-insights.adandeappolinaire.me

## Ce que nous avons fait

- Data : pipeline ETL reproductible vers `data/processed`.
- Analyses : notebooks exploratoires + rapports dans `reports/`.
- Modèles d'analyse : modules NLP et statistiques (BERTopic pour topics, spaCy pour NER, Isolation Forest pour anomalies, géospatial) dans `src/models/`.
- Modèle de prédiction : modèle Random Forest pour prédire l'ampleur des événements (entraînement/score dans `models/`).
- Tests : suite `pytest` sur les modeles et validations critiques.
- CI/CD : CI (tests + smoke checks) et CD (build/push image + deploy dashboard).

## Getting started

### Sans Docker

```bash
git clone https://github.com/Rabbi-GEEK/benin-insights-challenge-team2
cd benin-insights-challenge-team2

python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate
pip install -r requirements.txt
python pipeline/main.py
streamlit run dashboard/app.py
```

> **Les donnees brutes sont deja dans `data/raw/` — pas besoin de BigQuery.**  
> Les commandes ci-dessus regenerent `data/processed/` depuis `data/raw/`.

### Avec Docker (dashboard)

```bash
git clone https://github.com/Rabbi-GEEK/benin-insights-challenge-team2
cd benin-insights-challenge-team2
docker compose -f docker-compose.streamlit.yml up --build
```

L'app est exposee sur `http://localhost:8503` (ou `DASHBOARD_PORT`).

---

## Structure

```
├── .github/                # CI/CD config
├── dashboard/              # App Streamlit (app.py, components, views, static)
├── data/
│   ├── raw/                # Données brutes
│   └── processed/          # Données nettoyées et agrégées
├── docs/                   # Dossier de soumission et specs
├── models/                 # (media_model/) Entrainement et evaluation ML
├── notebooks/              # Analyses exploratoires (eda, ml_models, ...)
├── pipeline/               # ETL (extract/transform/load)
├── reports/                # Rapports, figures, CSV
├── src/                    # Modules Python, tests, visualisation
├── Dockerfile.streamlit    # Docker image dashboard
├── docker-compose.streamlit.yml
├── requirements.txt
├── Makefile
├── pytest.ini
└── README.md
```

## Équipe et Rôles

| Rôle | Réalisations principales | Démarche |
|------|------------------------|----------|
| **Data Engineer** | • Extraction GDELT (5089 événements sur 15 mois)<br>• Pipeline de nettoyage avec validation dates/types<br>• Agrégats mensuels pour ML (volume, tonalité, Goldstein)<br>• Dockerisation dashboard Streamlit | Validation `data/raw/gdelt_benin_main.csv`, génération `data/processed/`, tests reproductibilité |
| **Data Analyst** | • Analyse temporelle (pics jan 2025: 705 événements)<br>• Cartographie géospatiale des événements<br>• Dashboard interactif avec KPI et filtres<br>• Identification acteurs principaux (ECOWAS, ONU, Banque Mondiale) | EDA dans `notebooks/eda.ipynb`, visualisations dans `reports/`, intégration dashboard |
| **Data Scientist** | • Analyse tendances géopolitiques béninoises<br>• Interprétation anomalies (déc 2025: tonalité -2.77)<br>• Synthèse thématiques récurrentes (coopération, protestations)<br>• Rapport analyse avec insights actionnables | Cadrage depuis données GDELT, validation croisée, argumentation avec preuves |
| **ML Engineer** | • **BERTopic** : 6 thèmes identifiés (consultation, aide, protestation)<br>• **NER spaCy** : 237 personnes, 608 organisations, 31 lieux extraits<br>• **Isolation Forest** : 2 mois anormaux détectés (déc 2025, mai 2026)<br>• **Random Forest** : Prédiction impact média (features: Goldstein, EventRoot, international) | Dataset ML depuis `data/processed/`, entraînement dans `notebooks/ml_models.ipynb`, artefacts dans `models/` |

---


