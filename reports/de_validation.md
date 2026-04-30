# Validation Data Engineer — GDELT Bénin
> Auteur : MEDEHO TOTTIN Maurias — Data Engineer  
> Date : 2026-04-30  
> Pipeline : `make run` — 15/15 datasets générés sans erreur

---

## DE-01 — Cadrage validé

| Paramètre | Valeur |
|---|---|
| Période | 2025-01-01 → 2026-04-28 |
| Durée | 16 mois |
| Filtre pays action | `ActionGeo_CountryCode = 'BN'` |
| Filtre pays acteur | `Actor1CountryCode = 'BEN'` |
| Événements bruts | 8 082 |
| Après déduplication | 6 647 |

### Distribution mensuelle

| Mois | Événements | Note |
|---|---|---|
| 2025-01 | 532 | |
| 2025-02 | 363 | |
| 2025-03 | 442 | |
| 2025-04 | 421 | |
| 2025-05 | 426 | |
| 2025-06 | 209 |  creux médiatique estival (normal GDELT) |
| 2025-07 | 465 | |
| 2025-08 | 324 | |
| 2025-09 | 330 | |
| 2025-10 | 373 | |
| 2025-11 | 424 | |
| 2025-12 | 901 |  pic tentative de coup d'État |
| 2026-01 | 337 | |
| 2026-02 | 335 | |
| 2026-03 | 343 | |
| 2026-04 | 422 | |
| **Total** | **6 647** | |

**Conclusion :** aucun mois anormal. Le creux de juin 2025 est un artefact connu de GDELT (baisse de couverture médiatique estivale). Le pic de décembre 2025 est cohérent avec la tentative de coup d'État — validé par `zoom_dec2025.csv` (863 événements).

---

## DE-02 — Extraction validée

- `queries.sql` documenté — 15 requêtes couvrant les 10 angles d'analyse
- `data/raw/gdelt_benin_main.csv` régénérable via `USE_BIGQUERY=true` dans `.env`
- Toutes les colonnes nécessaires exportées (SQLDATE, Actor1/2, EventRootCode, GoldsteinScale, AvgTone, coordonnées GPS, SOURCEURL)

---

## DE-03 — Nettoyage & agrégats validés

- 15/15 datasets `data/processed/` générés sans erreur
- Traitements appliqués : parsing dates, normalisation CAMEO, nettoyage acteurs, flag sentiment, déduplication
- `reports/quality_report.json` : **0 erreur · 0 warning**

---

## DE-04 — Reproductibilité assurée

- Pipeline one-shot testé depuis zéro ce jour :
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
| Data Analyst | `data/processed/` (15 CSV) + `notebooks/` |
| Data Scientist | `gdelt_benin_clean.csv` — 6 647 lignes · 22 colonnes |
| ML Engineer | `data/processed/parquet/` — Parquet prêts |

---

> Repo : https://github.com/Maurigeek/benin-insights-challenge-team2
