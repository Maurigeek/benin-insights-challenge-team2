-- =============================================================
-- GDELT × Bénin Insights Challenge — Team 2
-- Fichier : pipeline/queries.sql
-- Auteur  : Data Engineer
-- Date    : 2026-04-28
-- Description : Toutes les requêtes SQL pour couvrir  10
--               angles d'analyse sur le Bénin (jan 2025 – avr 2026)
--               Cibles : journaliste, chercheur, décideur public
-- =============================================================
-- IMPORTANT : Toujours filtrer sur YEAR en premier pour
--             préserver le quota BigQuery (1 TB/mois)
-- Code pays Bénin : ActionGeo_CountryCode = 'BN'
--                   Actor1CountryCode = 'BEN'
-- =============================================================


-- -------------------------------------------------------------
-- REQUÊTE 0 : Test de connexion
-- -------------------------------------------------------------
SELECT *
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
LIMIT 10;


-- =============================================================
-- BLOC 1 — DONNÉES DE BASE
-- =============================================================

-- -------------------------------------------------------------
-- REQUÊTE 1 : Échantillon principal — données brutes Bénin
-- Angles    : tous
-- Sortie    : data/raw/gdelt_benin_main.csv
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
  AND YEAR >= 2025
LIMIT 10000;


-- -------------------------------------------------------------
-- REQUÊTE 2 : Évolution du ton médiatique mensuel
-- Angles    : 1 (instabilité politique), 4 (image médias)
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
-- Angles    : 3, 6, 10
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
-- REQUÊTE 4 : Événements par type
-- Angles    : tous — classification de base pour ML
-- Référence EventRootCode :
--   01=Déclarations  02=Appels  03=Coopération
--   04=Diplomatie    05=Engagement matériel
--   06=Échanges dipl 07=Coopération mat  08=Conflit verbal
--   09=Assaut        10=Coercition       11=Sanctions
--   12=Force         13=Violence armée   14=Violence masse
--   18=Arrestation   19=Violence non létale
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
-- REQUÊTE 5 : Événements géolocalisés
-- Angles    : 2, 7, 9
-- Note      : Coordonnées génériques (9.5, 2.25) exclues
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


-- =============================================================
-- BLOC 2 — ÉVÉNEMENTS CLÉS
-- =============================================================

-- -------------------------------------------------------------
-- REQUÊTE 6 : Zoom décembre 2025 — tentative de coup d'état
-- Angles    : 1 (instabilité politique)
-- Insight   : 1 097 événements · ton –2.57 · Colonel Pascal Tigri
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
-- Angles    : 1 (instabilité politique)
-- Insight   : Wadagni 94% · soupçons bourrage urnes (Le Parisien)
--             Al Jazeera, Bloomberg, Le Monde, CNBC Africa
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


-- =============================================================
-- BLOC 3 — ANGLES THÉMATIQUES
-- =============================================================

-- -------------------------------------------------------------
-- REQUÊTE 8 : Culture, tourisme et soft power
-- Angles    : 5, 9
-- Insight   : Forbes, Yahoo Travel, BBC, Hollywood Reporter
--             Ouidah · Abomey · Ganvie · Cuba partenaire
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
  AND EventRootCode IN ('05', '06', '07')
  AND AvgTone > 0
ORDER BY NumArticles DESC
LIMIT 3000;


-- -------------------------------------------------------------
-- REQUÊTE 9 : Coopération Bénin-Nigeria
-- Angle     : 6
-- Insight   : Lutte commune terrorisme · réouverture frontières
--             Fermeture frontières Kwara/Lagos (trafic armes)
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor1CountryCode,
  Actor2Name,
  Actor2CountryCode,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND (
    (Actor1CountryCode = 'BEN' AND Actor2CountryCode = 'NGA')
    OR
    (Actor1CountryCode = 'NGA' AND Actor2CountryCode = 'BEN')
  )
ORDER BY SQLDATE DESC
LIMIT 3000;


-- -------------------------------------------------------------
-- REQUÊTE 10 : Sécurité au nord — rempart jihadiste
-- Angles    : 2, 7
-- Insight   : 54 soldats tués · Al Qaeda · ISIS · Kofonou
--             Bénin = dernier rempart côtier face au Sahel
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
  AND YEAR >= 2025
  AND EventRootCode IN ('13', '14', '18', '19')
  AND (
    ActionGeo_FullName LIKE '%Alibori%'
    OR ActionGeo_FullName LIKE '%Borgou%'
    OR ActionGeo_FullName LIKE '%Atakora%'
    OR ActionGeo_FullName LIKE '%Karimama%'
    OR ActionGeo_FullName LIKE '%Kofouno%'
    OR ActionGeo_FullName LIKE '%Banikoara%'
    OR ActionGeo_FullName LIKE '%Kandi%'
    OR ActionGeo_FullName LIKE '%Natitingou%'
  )
ORDER BY SQLDATE DESC
LIMIT 2000;


-- -------------------------------------------------------------
-- REQUÊTE 11 : Femmes et société civile — VERSION CORRIGÉE
-- Angle     : 8
-- Note      : Requête précédente = 0 résultat car GDELT ne code
--             pas le genre dans Actor1Name/Actor2Name
--             Nouvelle approche : EventCode lié aux droits civils
--             + zones nord + sources spécialisées connues
-- Insight   : SwissInfo Banikoara · GAVI Parakou · MGF
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
  AND YEAR >= 2025
  AND (
    Actor1Name LIKE '%CIVIL%'
    OR Actor1Name LIKE '%NGO%'
    OR Actor1Name LIKE '%HEALTH%'
    OR Actor2Name LIKE '%CIVIL%'
    OR Actor2Name LIKE '%NGO%'
    OR Actor2Name LIKE '%HEALTH%'
    OR Actor2Name LIKE '%UNITED NATIONS%'
    OR Actor2Name LIKE '%UNICEF%'
    OR Actor2Name LIKE '%WHO%'
    OR SOURCEURL LIKE '%swissinfo%'
    OR SOURCEURL LIKE '%gavi%'
    OR SOURCEURL LIKE '%unhcr%'
    OR SOURCEURL LIKE '%unicef%'
  )
ORDER BY SQLDATE DESC
LIMIT 2000;


-- -------------------------------------------------------------
-- REQUÊTE 12 : La Chine silencieuse au Bénin
-- Angle     : 10
-- Insight   : 4e mission coton Parakou · présence agricole
--             Chine discrète vs France bruyante
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor1CountryCode,
  Actor2Name,
  Actor2CountryCode,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND (
    Actor1CountryCode = 'CHN'
    OR Actor2CountryCode = 'CHN'
  )
ORDER BY SQLDATE DESC
LIMIT 2000;


-- =============================================================
-- BLOC 4 — PERSONNALITÉS
-- =============================================================

-- -------------------------------------------------------------
-- REQUÊTE 13 : Personnalités béninoises clés
-- Angle     : tous — enrichissement avec noms réels
-- Couvre    : Talon (113) · Wadagni (67) · Kémi Séba (61)
--             Tigri (29) · Boko/Homeky (11) · Azannai (6)
--             Soglo (17) · Vlavonou (6) · Hounsou (9)
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
  AND YEAR >= 2025
  AND (
    LOWER(SOURCEURL) LIKE '%talon%'
    OR LOWER(SOURCEURL) LIKE '%wadagni%'
    OR LOWER(SOURCEURL) LIKE '%kemi-seba%'
    OR LOWER(SOURCEURL) LIKE '%kemi%seba%'
    OR LOWER(SOURCEURL) LIKE '%tigri%'
    OR LOWER(SOURCEURL) LIKE '%boko%'
    OR LOWER(SOURCEURL) LIKE '%homeky%'
    OR LOWER(SOURCEURL) LIKE '%azannai%'
    OR LOWER(SOURCEURL) LIKE '%soglo%'
    OR LOWER(SOURCEURL) LIKE '%hounsou%'
    OR LOWER(SOURCEURL) LIKE '%vlavonou%'
    OR LOWER(SOURCEURL) LIKE '%seidou%'
    OR Actor1Name LIKE '%TALON%'
    OR Actor1Name LIKE '%WADAGNI%'
    OR Actor1Name LIKE '%SOGLO%'
    OR Actor1Name LIKE '%SEIDOU%'
    OR Actor1Name LIKE '%LAFIA%'
    OR Actor1Name LIKE '%ZOSSOU%'
  )
ORDER BY NumArticles DESC
LIMIT 3000;


-- -------------------------------------------------------------
-- REQUÊTE 14 : Personnalités étrangères influençant le Bénin
-- Angle     : 3 (géopolitique), 7 (sécurité)
-- Couvre    : Tinubu (250) · Macron (15) · Traoré (8)
--             Ouattara (4) · Bazoum · Tchiani
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor1CountryCode,
  Actor2Name,
  Actor2CountryCode,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND (
    LOWER(SOURCEURL) LIKE '%tinubu%'
    OR LOWER(SOURCEURL) LIKE '%macron%'
    OR LOWER(SOURCEURL) LIKE '%traore%'
    OR LOWER(SOURCEURL) LIKE '%ouattara%'
    OR LOWER(SOURCEURL) LIKE '%bazoum%'
    OR LOWER(SOURCEURL) LIKE '%tchiani%'
    OR Actor1Name LIKE '%MACRON%'
    OR Actor1Name LIKE '%TINUBU%'
    OR Actor2Name LIKE '%MACRON%'
    OR Actor2Name LIKE '%TINUBU%'
  )
ORDER BY NumArticles DESC
LIMIT 2000;


-- -------------------------------------------------------------
-- REQUÊTE 15 : Liberté de presse et répression civile
-- Angle     : informations cachées aux Béninois
-- Insight   : RSF · IFEX · arrestation Sossoukpè
--             Mandat 7 ans · Cour constitutionnelle
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
  AND YEAR >= 2025
  AND EventRootCode IN ('17', '18', '15', '16')
  AND (
    Actor2Name LIKE '%JOURNALIST%'
    OR Actor2Name LIKE '%ACTIVIST%'
    OR Actor2Name LIKE '%OPPOSITION%'
    OR Actor2Name LIKE '%DEMOCRATIC%'
    OR SOURCEURL LIKE '%rsf%'
    OR SOURCEURL LIKE '%ifex%'
    OR SOURCEURL LIKE '%amnesty%'
    OR SOURCEURL LIKE '%hrw%'
    OR SOURCEURL LIKE '%constitution%'
    OR SOURCEURL LIKE '%mandat%'
  )
ORDER BY AvgTone ASC
LIMIT 2000;


-- REQUÊTE 16 : CAN 2025 — sport et image internationale
SELECT SQLDATE, Actor1Name, Actor1CountryCode, Actor2Name,
       Actor2CountryCode, EventRootCode, GoldsteinScale,
       AvgTone, NumArticles, ActionGeo_FullName, SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND (
    Actor1CountryCode = 'EGY'
    OR Actor2CountryCode = 'EGY'
    OR LOWER(SOURCEURL) LIKE '%afcon%'
    OR LOWER(SOURCEURL) LIKE '%africa-cup%'
    OR LOWER(SOURCEURL) LIKE '%coppa-dafrica%'
  )
ORDER BY SQLDATE DESC
LIMIT 2000;

-- REQUÊTE 17 : Économie et développement
SELECT SQLDATE, Actor1Name, Actor2Name, EventRootCode,
       GoldsteinScale, AvgTone, NumArticles,
       ActionGeo_FullName, SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND (
    LOWER(SOURCEURL) LIKE '%ecofinagency%'
    OR LOWER(SOURCEURL) LIKE '%bloomberg%'
    OR LOWER(SOURCEURL) LIKE '%reuters%'
    OR LOWER(SOURCEURL) LIKE '%imf.org%'
    OR LOWER(SOURCEURL) LIKE '%worldbank%'
    OR LOWER(SOURCEURL) LIKE '%afdb%'
  )
ORDER BY SQLDATE DESC
LIMIT 2000;

-- REQUÊTE 18 : Sources officielles — ECOWAS + gouvernement béninois
SELECT SQLDATE, Actor1Name, Actor2Name, EventRootCode,
       GoldsteinScale, AvgTone, NumArticles,
       ActionGeo_FullName, SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND (
    LOWER(SOURCEURL) LIKE '%ecowas.int%'
    OR LOWER(SOURCEURL) LIKE '%gouv.bj%'
    OR LOWER(SOURCEURL) LIKE '%presidence.bj%'
  )
ORDER BY SQLDATE DESC
LIMIT 2000;

-- -------------------------------------------------------------
-- REQUÊTE 19 : Médias béninois — narrative interne
-- Angle     : Ce que la presse béninoise dit du Bénin
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor1CountryCode,
  Actor2Name,
  Actor2CountryCode,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND (
    LOWER(SOURCEURL) LIKE '%gouv.bj%'
    OR LOWER(SOURCEURL) LIKE '%lanouvelletribune.info%'
    OR LOWER(SOURCEURL) LIKE '%24haubenin.info%'
    OR LOWER(SOURCEURL) LIKE '%promptnewsonline.com%'
    OR LOWER(SOURCEURL) LIKE '%beninactu.net%'
    OR LOWER(SOURCEURL) LIKE '%matinlibre.com%'
    OR LOWER(SOURCEURL) LIKE '%fraternite.info%'
    OR LOWER(SOURCEURL) LIKE '%acotonou.com%'
    OR LOWER(SOURCEURL) LIKE '%beninwebtv.com%'
    OR LOWER(SOURCEURL) LIKE '%presidence.bj%'
  )
ORDER BY SQLDATE DESC
LIMIT 3000;


-- -------------------------------------------------------------
-- REQUÊTE 20 : Médias internationaux — narrative externe
-- Angle     : Ce que la presse mondiale dit du Bénin
--             (hors médias béninois et bruit Nigeria)
-- -------------------------------------------------------------
SELECT
  SQLDATE,
  Actor1Name,
  Actor1CountryCode,
  Actor2Name,
  Actor2CountryCode,
  EventRootCode,
  GoldsteinScale,
  AvgTone,
  NumArticles,
  ActionGeo_FullName,
  SOURCEURL
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BN'
  AND YEAR >= 2025
  AND LOWER(SOURCEURL) NOT LIKE '%gouv.bj%'
  AND LOWER(SOURCEURL) NOT LIKE '%lanouvelletribune.info%'
  AND LOWER(SOURCEURL) NOT LIKE '%24haubenin.info%'
  AND LOWER(SOURCEURL) NOT LIKE '%beninactu.net%'
  AND LOWER(SOURCEURL) NOT LIKE '%presidence.bj%'
  AND LOWER(SOURCEURL) NOT LIKE '%punchng.com%'
  AND LOWER(SOURCEURL) NOT LIKE '%dailypost.ng%'
  AND LOWER(SOURCEURL) NOT LIKE '%premiumtimesng.com%'
  AND LOWER(SOURCEURL) NOT LIKE '%vanguardngr.com%'
  AND LOWER(SOURCEURL) NOT LIKE '%thenationonlineng.net%'
  AND LOWER(SOURCEURL) NOT LIKE '%channelstv.com%'
  AND LOWER(SOURCEURL) NOT LIKE '%thisdaylive.com%'
  AND LOWER(SOURCEURL) NOT LIKE '%nigerianobservernews.com%'
  AND LOWER(SOURCEURL) NOT LIKE '%guardian.ng%'
  AND LOWER(SOURCEURL) NOT LIKE '%thesun.ng%'
  AND LOWER(SOURCEURL) NOT LIKE '%leadership.ng%'
  AND LOWER(SOURCEURL) NOT LIKE '%legit.ng%'
  AND LOWER(SOURCEURL) NOT LIKE '%dailytrust.com%'
ORDER BY NumArticles DESC
LIMIT 5000;