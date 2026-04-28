-- =============================================================
-- GDELT × Bénin Insights Challenge — Team 2
-- Fichier : pipeline/queries.sql
-- Auteur  : Data Engineer
-- Date    : 2026-04-28
-- Description : Toutes les requêtes SQL utilisées pour extraire
--               et analyser les données GDELT sur le Bénin
-- =============================================================
-- IMPORTANT : Toujours filtrer sur YEAR en premier pour
--             préserver le quota BigQuery (1TB/mois)
-- =============================================================


-- -------------------------------------------------------------
-- REQUÊTE 0 : Test de connexion rapide (vérification)
-- Objectif  : Vérifier que la connexion BigQuery fonctionne
-- Coût      : Très faible (~quelques KB)
-- -------------------------------------------------------------
SELECT *
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
LIMIT 10;


-- -------------------------------------------------------------
-- REQUÊTE 1 : Échantillon principal — données brutes Bénin
-- Objectif  : Extraire les événements où le Bénin est acteur
--             principal sur les 12 derniers mois
-- Sortie    : data/raw/gdelt_benin_main.csv
-- Note      : Filtre Actor1CountryCode = 'BEN' pour réduire
--             le bruit lié à Benin City (Nigeria)
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor1CountryCode,
  Actor2Name,
  Actor2CountryCode,
  EventCode,
  EventBaseCode,
  EventRootCode,
  GoldsteinScale,
  NumArticles,
  AvgTone,
  ActionGeo_FullName,
  ActionGeo_CountryCode,
  ActionGeo_Lat,
  ActionGeo_Long,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND Actor1CountryCode = 'BEN'
  AND YEAR >= 2025
LIMIT 10000;


-- -------------------------------------------------------------
-- REQUÊTE 2 : Évolution du ton médiatique mensuel
-- Objectif  : Mesurer comment les médias parlent du Bénin
--             mois par mois (positif / négatif)
-- Sortie    : data/processed/tone_monthly.csv
-- Insight   : Décembre 2025 = pic négatif (–2.57) lié à la
--             tentative de coup d'état
-- -------------------------------------------------------------
SELECT
  SUBSTR(CAST(SQLDATE AS STRING), 1, 6) AS mois,
  ROUND(AVG(AvgTone), 2)                AS ton_moyen,
  COUNT(*)                              AS nb_evenements
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND Actor1CountryCode = 'BEN'
  AND YEAR >= 2025
GROUP BY mois
ORDER BY mois;


-- -------------------------------------------------------------
-- REQUÊTE 3 : Pays qui interagissent avec le Bénin
-- Objectif  : Identifier quels pays sont les plus impliqués
--             dans les événements liés au Bénin
-- Sortie    : data/processed/actors_country.csv
-- Insight   : Nigeria (bruit), Niger (tensions), France, Chine
-- -------------------------------------------------------------
SELECT
  Actor2CountryCode,
  COUNT(*) AS nb_interactions
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND Actor1CountryCode = 'BEN'
  AND YEAR >= 2025
  AND Actor2CountryCode IS NOT NULL
  AND Actor2CountryCode != ''
GROUP BY Actor2CountryCode
ORDER BY nb_interactions DESC
LIMIT 20;


-- -------------------------------------------------------------
-- REQUÊTE 4 : Événements par type (EventRootCode)
-- Objectif  : Classifier les événements par grande catégorie
--             pour identifier les thèmes dominants
-- Sortie    : data/processed/events_by_type.csv
-- Référence EventRootCode :
--   01 = Déclarations verbales
--   02 = Appels / Demandes
--   03 = Coopération
--   04 = Consultations diplomatiques
--   05 = Engagement matériel
--   06 = Échanges diplomatiques
--   07 = Coopération matérielle
--   08 = Conflit verbal
--   09 = Assaut
--   10 = Coercition
--   11 = Sanctions / Pression
--   12 = Appels à la force
--   13 = Violence armée
--   14 = Violence de masse
--   18 = Arrestation / Détention
--   19 = Violence non létale
--   20 = Utilisation d'armes non conventionnelles
-- -------------------------------------------------------------
SELECT
  EventRootCode,
  COUNT(*)                     AS nb_evenements,
  ROUND(AVG(GoldsteinScale),2) AS stabilite_moyenne,
  ROUND(AVG(AvgTone), 2)       AS ton_moyen,
  SUM(NumArticles)             AS total_articles
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND Actor1CountryCode = 'BEN'
  AND YEAR >= 2025
GROUP BY EventRootCode
ORDER BY nb_evenements DESC;


-- -------------------------------------------------------------
-- REQUÊTE 5 : Événements géolocalisés (pour carte interactive)
-- Objectif  : Extraire les coordonnées GPS des événements
--             pour visualisation cartographique dans le dashboard
-- Sortie    : data/processed/geo_events.csv
-- Note      : Filtre sur lat/long non nuls pour éviter les
--             points génériques (9.5, 2.25) = tout le Bénin
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor2Name,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  ActionGeo_Lat,
  ActionGeo_Long,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND Actor1CountryCode = 'BEN'
  AND YEAR >= 2025
  AND ActionGeo_Lat IS NOT NULL
  AND ActionGeo_Long IS NOT NULL
  AND ActionGeo_Lat != 9.5
  AND ActionGeo_Long != 2.25
LIMIT 5000;


-- -------------------------------------------------------------
-- REQUÊTE 6 : Zoom décembre 2025 — tentative de coup d'état
-- Objectif  : Analyser en détail le pic d'événements de déc 2025
--             qui est le mois le plus couvert et le plus négatif
-- Usage     : Notebook 04_evenements_cles.ipynb
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor2Name,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND Actor1CountryCode = 'BEN'
  AND SQLDATE >= 20251201
  AND SQLDATE <= 20251231
ORDER BY NumArticles DESC
LIMIT 1000;


-- -------------------------------------------------------------
-- REQUÊTE 7 : Zoom élection présidentielle avril 2026
-- Objectif  : Analyser la couverture médiatique de l'élection
-- Usage     : Notebook 04_evenements_cles.ipynb
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor2Name,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND Actor1CountryCode = 'BEN'
  AND SQLDATE >= 20260401
  AND SQLDATE <= 20260428
ORDER BY NumArticles DESC
LIMIT 1000;