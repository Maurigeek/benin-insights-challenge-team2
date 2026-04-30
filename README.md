# 🇧🇯 Bénin Insights Challenge — Team 2
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
|   ├── main.py                 # Orchestrateur des 3 étapes
│   └── queries.sql             # Requêtes documentées
├── notebooks/                  # Analyses exploratoires
├── models/                     # Entraînement et évaluation ML
├── dashboard/                  # Application Streamlit
├── reports/                    # Insights et résumé exécutif
├── .env                        # Variables d'environnement locales (non versionné)
├── .env.example                # Template .env à copier
├── .gitignore
├── Makefile
└── requirements.txt
```

---


## Démarrage rapide

### Prérequis

- Python 3.11+
- `git`
- *(Optionnel — mode BigQuery)* Un compte GCP avec accès à `gdelt-bq.gdeltv2.events`

### Installation

```bash
git clone https://github.com/Maurigeek/benin-insights-challenge-team2
cd benin-insights-challenge-team2

# Copier et configurer les variables d'environnement
cp .env.example .env
# → Éditer .env si nécessaire (voir section Variables d'environnement)

# Créer le venv et installer les dépendances
make install
```

### Lancer la pipeline complète

> **Les données brutes sont déjà dans `data/raw/` — pas besoin de BigQuery.**  
> La commande ci-dessous régénère tout `data/processed/` depuis `data/raw/`.

```bash
make run
```

### Lancer le dashboard

```bash
make dashboard
```

### Commandes disponibles

| Commande | Description |
|---|---|
| `make install` | Crée le venv et installe les dépendances |
| `make run` | Lance la pipeline complète (extract → transform → load) |
| `make dashboard` | Lance l'application Streamlit | 
| `make reset` | Vide `data/processed/` pour forcer une régénération propre |
| `make clean` | Supprime le venv et les fichiers `.pyc` / `__pycache__` |

---

### Windows (sans Make)

```bash
git clone https://github.com/Maurigeek/benin-insights-challenge-team2
cd benin-insights-challenge-team2
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python pipeline/main.py
streamlit run dashboard/app.py
```

---

## Variables d'environnement

Copier `.env.example` - `.env` et adapter si besoin.

> **Mode BigQuery (`USE_BIGQUERY=true`)** : nécessite en plus la variable
> `GOOGLE_APPLICATION_CREDENTIALS` pointant vers un fichier de clé de service GCP,
> ou une authentification via `gcloud auth application-default login`.

---

## Pipeline — fonctionnement détaillé

```
data/raw/  ──►  extract.py  ──►  [BigQuery ou skip]
                     │
                     ▼
             transform.py   ──►  data/processed/   (CSV + Parquet + GeoJSON)
                     │
                     ▼
               load.py       ──►  reports/quality_report.json
```

### Étape 1 — Extraction (`extract.py`)

- En mode `USE_BIGQUERY=false` (défaut) : étape ignorée, les CSV de `data/raw/` sont utilisés directement.
- En mode `USE_BIGQUERY=true` : exécute les requêtes de `queries.sql` sur `gdelt-bq.gdeltv2.events` et écrit dans `data/raw/`.

### Étape 2 — Transformation (`transform.py`)

Toutes les transformations opèrent depuis `data/raw/` et écrivent dans `data/processed/`. La pipeline est **idempotente** : relancer `make run` après un `make reset` produit exactement le même résultat.

### Étape 3 — Chargement (`load.py`)

- Exporte les datasets principaux en **Parquet** (usage dashboard).
- Exporte les datasets géolocalisés en **GeoJSON** (cartes Plotly).
- Génère `reports/quality_report.json` avec stats de validation.

---

## Usage de l'IA

Ce projet utilise Claude (Anthropic) pour orienter l'exploration des données
et structurer l'architecture. Tout le code et les analyses sont produits
et validés par l'équipe.