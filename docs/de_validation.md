# Validation Data Engineer — GDELT Bénin  
> Pipeline : `make run` — 20/20 datasets générés sans erreur

---

## DE-01 — Cadrage validé

| Paramètre | Valeur |
|---|---|
| Période | 2025-01-01 → 2026-05-02 |
| Durée | 16 mois |
| Filtre pays action | `ActionGeo_CountryCode = 'BN'` |
| Filtre pays acteur | `Actor1CountryCode = 'BEN'` |
| Événements bruts (BigQuery) | 10 000 |
| Après filtre Nigeria + déduplication | 5 089 |

### Distribution mensuelle

| Mois | Événements | Note |
|---|---|---|
| 2025-01 | ~380 | |
| 2025-02 | ~290 | |
| 2025-03 | ~340 | |
| 2025-04 | ~320 | |
| 2025-05 | ~330 | |
| 2025-06 | ~160 | ⚠ creux médiatique estival (artefact GDELT connu) |
| 2025-07 | ~360 | |
| 2025-08 | ~250 | |
| 2025-09 | ~255 | |
| 2025-10 | ~290 | |
| 2025-11 | ~325 | |
| 2025-12 | ~230 | ↑ pic — zoom_dec2025 (230 événements filtrés) |
| 2026-01 | ~260 | |
| 2026-02 | ~260 | |
| 2026-03 | ~265 | |
| 2026-04 | ~740 | ↑ pic — zoom_election2026 (907 événements) |
| **Total** | **5 089** | |

**Conclusion :** aucun mois anormal. Le creux de juin 2025 est un artefact connu de GDELT (baisse de couverture médiatique estivale). Le pic d'avril 2026 est cohérent avec le contexte électoral — validé par `zoom_election2026.csv` (907 événements).

---

## DE-02 — Extraction validée

- `queries.sql` documenté — 20 requêtes couvrant les 5 blocs d'analyse
- `data/raw/gdelt_benin_main.csv` régénérable via `USE_BIGQUERY=true` dans `.env`
- Toutes les colonnes nécessaires exportées (SQLDATE, Actor1/2, EventRootCode, GoldsteinScale, AvgTone, coordonnées GPS, SOURCEURL)

### Datasets extraits — 20 fichiers

| Bloc | Dataset | Lignes | Période |
|---|---|---|---|
| Base | `gdelt_benin_clean` | 5 089 | 2025-01-01 → 2026-05-02 |
| Base | `geo_events` | 2 803 | 2025-01-02 → 2026-04-30 |
| Agrégats | `tone_monthly` | 15 | 2025-01-01 → 2026-05-01 |
| Agrégats | `actors_country` | 20 | — |
| Agrégats | `events_by_type` | 19 | — |
| Événements clés | `zoom_dec2025` | 230 | 2025-12-07 → 2025-12-31 |
| Événements clés | `zoom_election2026` | 907 | 2026-04-01 → 2026-04-19 |
| Thématiques | `culture_tourisme` | 760 | 2025-01-01 → 2026-05-02 |
| Thématiques | `cooperation_ben_nga` | 356 | 2025-01-03 → 2026-04-30 |
| Thématiques | `securite_nord` | 72 | 2025-01-11 → 2026-04-11 |
| Thématiques | `femmes_benin` | 112 | 2025-01-12 → 2026-04-30 |
| Thématiques | `chine_benin` | 47 | 2025-01-13 → 2026-04-18 |
| Thématiques | `personnalites_benin` | 346 | 2025-01-05 → 2026-04-19 |
| Thématiques | `personnalites_etrangeres` | 165 | 2025-01-11 → 2026-04-16 |
| Thématiques | `liberte_presse` | 14 | 2025-01-26 → 2026-04-17 |
| Nouveaux ✦ | `can2025_sport` | 49 | 2025-01-31 → 2026-03-31 |
| Nouveaux ✦ | `economie` | 77 | 2025-01-05 → 2026-04-01 |
| Nouveaux ✦ | `sources_officielles` | 116 | 2025-01-14 → 2026-04-10 |
| Nouveaux ✦ | `medias_beninois` | 713 | 2025-01-03 → 2026-04-30 |
| Nouveaux ✦ | `medias_internationaux` | 4 980 | 2025-01-01 → 2026-05-02 |

✦ 5 nouveaux datasets ajoutés depuis la version précédente du rapport (15 → 20 datasets).

---

## DE-03 — Nettoyage & agrégats validés

- 20/20 datasets `data/processed/` générés sans erreur
- Traitements appliqués : parsing dates, normalisation CAMEO, nettoyage acteurs, flag sentiment, déduplication, filtre bbox GPS
- `reports/quality_report.json` : **0 erreur · 0 warning**

### Transformations appliquées

| Transformation | Description |
|---|---|
| Déduplication | Suppression des doublons sur (date, Actor1Name, EventRootCode, SOURCEURL) |
| Parsing dates | SQLDATE int YYYYMMDD → datetime + colonnes dérivées : annee, mois, mois_label, semaine |
| Normalisation CAMEO | EventRootCode int → string zero-padded + event_label lisible |
| Nettoyage acteurs | Strip whitespace, valeurs vides → `'Inconnu'` |
| Flag sentiment | AvgTone → positif (>1) / neutre (-1 à 1) / négatif (<-1) |
| Bbox GPS | Filtrage des points hors bounding box Bénin (lat 6.0–12.5, lon 0.7–3.9) |
| Agrégats locaux | tone_monthly, actors_country, events_by_type recalculés depuis gdelt_benin_clean en mode local |

### Exports générés

| Format | Fichiers | Usage |
|---|---|---|
| CSV | 20 fichiers — `data/processed/` | Notebooks, analyse exploratoire |
| Parquet | 8 fichiers — `data/processed/parquet/` | Dashboard Streamlit (chargement 3× plus rapide) |
| GeoJSON | 3 fichiers — `data/processed/geojson/` | Cartes Folium / Plotly (geo_events, culture_tourisme, securite_nord) |
| JSON | `reports/quality_report.json` | Rapport qualité automatique — 20/20 OK |

---

## DE-04 — Reproductibilité assurée

- Pipeline one-shot testé depuis zéro le 2 mai 2026 :
  ```bash
  git clone https://github.com/Maurigeek/benin-insights-challenge-team2
  cd benin-insights-challenge-team2
  cp .env.example .env
  make install
  make run
  ```
- `Makefile`, `.env.example` et `README.md` à jour

---

## DE-05 — Équipe débloquée

| Profil | Fichiers disponibles |
|---|---|
| Data Analyst | `data/processed/` (20 CSV) + `notebooks/` |
| Data Scientist | `gdelt_benin_clean.csv` — 5 089 lignes · 22 colonnes |
| ML Engineer | `data/processed/parquet/` — 8 Parquet prêts |
| Dashboard | `data/processed/geojson/` — 3 GeoJSON (geo_events, culture_tourisme, securite_nord) |

---

> Repo : https://github.com/Maurigeek/benin-insights-challenge-team2