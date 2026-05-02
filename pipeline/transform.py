
import logging
import pandas as pd
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MAPPING CAMEO — EventRootCode → label lisible
# ---------------------------------------------------------------------------
CAMEO_LABELS = {
    "01": "Déclaration publique",
    "02": "Appel / Demande",
    "03": "Coopération",
    "04": "Consultation",
    "05": "Engagement diplomatique",
    "06": "Coopération matérielle",
    "07": "Aide / Assistance",
    "08": "Accord / Coopération",
    "09": "Médiation",
    "10": "Demande / Aide",
    "11": "Désapprobation",
    "12": "Rejet / Refus",
    "13": "Menace",
    "14": "Protestation",
    "15": "Force non militaire",
    "16": "Réduction des relations",
    "17": "Coercition",
    "18": "Assaut",
    "19": "Violence de masse",
    "20": "Usage d'armes non conventionnelles",
}


# ---------------------------------------------------------------------------
# UTILITAIRES PARTAGÉS
# ---------------------------------------------------------------------------

def load(path: str, label: str) -> pd.DataFrame | None:
    """Charge un CSV avec logging. Retourne None si le fichier est absent."""
    p = Path(path)
    if not p.exists():
        logger.warning(f"[{label}] Fichier introuvable : {path}")
        return None
    df = pd.read_csv(path)
    logger.info(f"[{label}] Chargé — {len(df)} lignes")
    return df


def save(df: pd.DataFrame, path: str, label: str) -> None:
    """Sauvegarde un DataFrame en CSV avec logging."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    logger.info(f"[{label}] Sauvegardé — {len(df)} lignes → {path}")


def parse_sqldate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convertit SQLDATE (int YYYYMMDD) en datetime et ajoute
    les colonnes dérivées : date, annee, mois, mois_label, semaine.
    Si SQLDATE est absent (fichier déjà transformé), opère sur 'date' existant.
    """
    df = df.copy()

    if "SQLDATE" in df.columns:
        df["date"] = pd.to_datetime(df["SQLDATE"].astype(str), format="%Y%m%d", errors="coerce")
        df = df.drop(columns=["SQLDATE"])
    elif "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        raise ValueError("Colonne 'SQLDATE' ou 'date' introuvable dans le DataFrame.")

    df["annee"]      = df["date"].dt.year
    df["mois"]       = df["date"].dt.month
    df["mois_label"] = df["date"].dt.strftime("%b %Y")
    df["semaine"]    = df["date"].dt.isocalendar().week.astype(int)
    return df


def normalize_event_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise EventRootCode int → string zero-padded (1 → '01')
    et ajoute la colonne event_label depuis le mapping CAMEO.
    """
    df = df.copy()
    if "EventRootCode" in df.columns:
        df["EventRootCode"] = df["EventRootCode"].astype(str).str.zfill(2)
        df["event_label"]   = df["EventRootCode"].map(CAMEO_LABELS).fillna("Inconnu")
    return df


def clean_actors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie Actor1Name / Actor2Name :
    - Strip whitespace
    - Remplace les chaînes vides par NaN
    - Fillna → 'Inconnu'
    """
    df = df.copy()
    for col in ["Actor1Name", "Actor2Name", "Actor1CountryCode", "Actor2CountryCode"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA})
            df[col] = df[col].fillna("Inconnu")
    return df


def flag_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute une colonne sentiment catégorielle basée sur AvgTone :
        positif  : AvgTone > 1
        neutre   : -1 <= AvgTone <= 1
        négatif  : AvgTone < -1
    """
    if "AvgTone" not in df.columns:
        return df
    df = df.copy()
    df["sentiment"] = pd.cut(
        df["AvgTone"],
        bins=[-float("inf"), -1, 1, float("inf")],
        labels=["négatif", "neutre", "positif"],
    )
    return df


def drop_duplicates_strict(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    """Supprime les doublons stricts sur un subset de colonnes."""
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first")
    dropped = before - len(df)
    if dropped:
        logger.info(f"  Doublons supprimés : {dropped}")
    return df


def _base_transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transformations communes à tous les datasets thématiques :
    parse date → normalise EventRootCode → nettoie acteurs →
    flag sentiment → déduplication.
    """
    df = parse_sqldate(df)
    df = normalize_event_code(df)
    df = clean_actors(df)
    df = flag_sentiment(df)
    dedup_cols = [c for c in ["date", "Actor1Name", "EventRootCode", "SOURCEURL"] if c in df.columns]
    df = drop_duplicates_strict(df, subset=dedup_cols)
    return df
 
 
def _filter_year(df: pd.DataFrame, year_min: int = 2025) -> pd.DataFrame:
    """Filtre SQLDATE >= year_min * 10000 (équivalent YEAR >= 2025 en BigQuery)."""
    if "SQLDATE" in df.columns:
        return df[df["SQLDATE"] >= year_min * 10_000].copy()
    # Si déjà parsé en date
    if "date" in df.columns:
        return df[pd.to_datetime(df["date"], errors="coerce").dt.year >= year_min].copy()
    return df.copy()


# ---------------------------------------------------------------------------
# TRANSFORMATIONS SPÉCIFIQUES PAR DATASET
# ---------------------------------------------------------------------------

def transform_main(df: pd.DataFrame) -> pd.DataFrame:
    """
    gdelt_benin_main — dataset principal.
    - Déduplication sur (date, Actor1Name, EventCode, SOURCEURL)
    - Parsing date + colonnes dérivées
    - Normalisation EventRootCode
    - Nettoyage acteurs
    - Flag sentiment
    """
    # Filtre bruit Nigeria — Benin City / Edo State

    NIGERIAN_NOISE_DOMAINS = [
        'punchng.com', 'dailypost.ng', 'premiumtimesng.com',
        'vanguardngr.com', 'thenationonlineng.net', 'channelstv.com',
        'thisdaylive.com', 'nigerianobservernews.com', 'guardian.ng',
        'thesun.ng', 'leadership.ng', 'nationalaccordnewspaper.com',
        'theeagleonline.com.ng', 'blueprint.ng', 'thecable.ng',
        'legit.ng', 'thenewsnigeria.com.ng', 'tell.ng',
        'hallmarknews.com', 'pmnewsnigeria.com', 'nigerianeye.com',
        'dailytrust.com', 'tribuneonlineng.com', 'sunnewsonline.com'
    ]

    pattern = '|'.join(NIGERIAN_NOISE_DOMAINS)
    before = len(df)
    df = df[~df['SOURCEURL'].str.contains(pattern, case=False, na=False)]
    print(f"Doublons supprimés : {before - len(df)}")
    logger.info(f"Bruit Nigeria supprimé : {before - len(df)} lignes")

    df = drop_duplicates_strict(df, subset=["SQLDATE", "Actor1Name", "EventCode", "SOURCEURL"])
    df = parse_sqldate(df)
    df = normalize_event_code(df)
    df = clean_actors(df)
    df = flag_sentiment(df)
    return df


def transform_events_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    events_by_type — normalisation EventRootCode + labels CAMEO.
    """
    df = normalize_event_code(df)
    df = df.sort_values("nb_evenements", ascending=False).reset_index(drop=True)
    return df


def transform_geo(df: pd.DataFrame) -> pd.DataFrame:
    """
    geo_events — parsing date + nettoyage acteurs.
    Pas de déduplication : chaque point géographique est intentionnel.
    """
    df = parse_sqldate(df)
    df = normalize_event_code(df)
    df = clean_actors(df)
    df = flag_sentiment(df)
    return df


def compute_tone_monthly(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Recalcule tone_monthly depuis gdelt_benin_clean.
    Équivalent local de la requête BigQuery GROUP BY mois.
    """
    df = df_clean.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["mois_yyyymm"] = df["date"].dt.to_period("M").astype(str)
    agg = (
        df.groupby("mois_yyyymm")
        .agg(
            ton_moyen=("AvgTone", "mean"),
            nb_evenements=("AvgTone", "count"),
        )
        .round(2)
        .reset_index()
        .rename(columns={"mois_yyyymm": "mois"})
    )
    agg["date"]       = pd.to_datetime(agg["mois"], format="%Y-%m", errors="coerce")
    agg["mois_label"] = agg["date"].dt.strftime("%b %Y")
    return agg.sort_values("date").reset_index(drop=True)


def compute_actors_country(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Recalcule actors_country depuis gdelt_benin_clean.
    Équivalent local de la requête BigQuery GROUP BY Actor2CountryCode.
    """
    df = df_clean[
        df_clean["Actor2CountryCode"].notna() &
        (df_clean["Actor2CountryCode"] != "Inconnu") &
        (df_clean["Actor2CountryCode"] != "")
    ].copy()
    agg = (
        df.groupby("Actor2CountryCode")
        .size()
        .reset_index(name="nb_interactions")
        .sort_values("nb_interactions", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    return agg


def compute_events_by_type(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Recalcule events_by_type depuis gdelt_benin_clean.
    Équivalent local de la requête BigQuery GROUP BY EventRootCode.
    """
    agg = (
        df_clean.groupby("EventRootCode")
        .agg(
            nb_evenements=("EventRootCode", "count"),
            stabilite_moyenne=("GoldsteinScale", "mean"),
            ton_moyen=("AvgTone", "mean"),
            total_articles=("NumArticles", "sum"),
        )
        .round(2)
        .reset_index()
        .sort_values("nb_evenements", ascending=False)
        .reset_index(drop=True)
    )
    # Réappliquer les labels CAMEO
    agg = normalize_event_code(agg)
    return agg


def compute_zoom_dec2025(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Zoom sur décembre 2025 — tentative de coup d'État.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 6 (queries.sql).
    """
    df = df_raw.copy()
    df = df[
        (df["SQLDATE"] >= 20_251_201) &
        (df["SQLDATE"] <= 20_251_231)
    ]
    df = _base_transform(df)
    df = df.sort_values("NumArticles", ascending=False).head(1_000).reset_index(drop=True)
    return df
 
 
def compute_zoom_election2026(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Zoom sur l'élection présidentielle d'avril 2026.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 7 (queries.sql).
    """
    df = df_raw.copy()
    df = df[
        (df["SQLDATE"] >= 20_260_401) &
        (df["SQLDATE"] <= 20_260_428)
    ]
    df = _base_transform(df)
    df = df.sort_values("NumArticles", ascending=False).head(1_000).reset_index(drop=True)
    return df
 
 
def compute_culture_tourisme(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Culture, tourisme et soft power (ton positif).
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 8 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    # Normalisation préalable pour pouvoir filtrer sur les codes
    df["EventRootCode"] = df["EventRootCode"].astype(str).str.zfill(2)
    df = df[df["EventRootCode"].isin(["05", "06", "07"])]
    df = df[df["AvgTone"] > 0]
 
    df = _base_transform(df)
    df = df.sort_values("NumArticles", ascending=False).head(3_000).reset_index(drop=True)
    return df
 
 
def compute_cooperation_ben_nga(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Coopération bilatérale Bénin–Nigeria (tous sens).
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 9 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    mask_ben_nga = (
        (df["Actor1CountryCode"] == "BEN") & (df["Actor2CountryCode"] == "NGA")
    )
    mask_nga_ben = (
        (df["Actor1CountryCode"] == "NGA") & (df["Actor2CountryCode"] == "BEN")
    )
    df = df[mask_ben_nga | mask_nga_ben]
 
    df = _base_transform(df)
    df = df.sort_values("date", ascending=False).head(3_000).reset_index(drop=True)
    return df
 

def compute_securite_nord_thematic(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Sécurité au nord — version thématique complète depuis raw.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 10 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    df["EventRootCode"] = df["EventRootCode"].astype(str).str.zfill(2)
    df = df[df["EventRootCode"].isin(["13", "14", "18", "19"])]
 
    localites_nord = (
        "Alibori|Borgou|Atakora|Donga|Karimama|Kofouno|Banikoara|Kandi|Natitingou"
    )
    df = df[
        df["ActionGeo_FullName"].str.contains(localites_nord, case=False, na=False)
    ]
 
    df = _base_transform(df)
    df = df.sort_values("date", ascending=False).head(2_000).reset_index(drop=True)
    return df


def compute_femmes_benin(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Femmes et société civile.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 11 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    # Normalisation des colonnes texte pour le filtre LIKE
    a1  = df["Actor1Name"].astype(str).str.upper()
    a2  = df["Actor2Name"].astype(str).str.upper()
    url = df["SOURCEURL"].astype(str).str.lower()
 
    keywords_actors  = ["CIVIL", "NGO", "HEALTH", "UNITED NATIONS", "UNICEF", "WHO"]
    keywords_sources = ["swissinfo", "gavi", "unhcr", "unicef"]
 
    mask_actors = (
        a1.str.contains("|".join(keywords_actors), na=False) |
        a2.str.contains("|".join(keywords_actors), na=False)
    )
    mask_sources = url.str.contains("|".join(keywords_sources), na=False)
 
    df = df[mask_actors | mask_sources]
    df = _base_transform(df)
    df = df.sort_values("date", ascending=False).head(2_000).reset_index(drop=True)
    return df
 
 
def compute_chine_benin(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Présence chinoise au Bénin.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 12 (queries.sql).
    """
    df = _filter_year(df_raw)
    df = df[
        (df["Actor1CountryCode"] == "CHN") |
        (df["Actor2CountryCode"] == "CHN")
    ]
    df = _base_transform(df)
    df = df.sort_values("date", ascending=False).head(2_000).reset_index(drop=True)
    return df
 

def compute_personnalites_benin(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Personnalités béninoises clés (Talon, Wadagni, Kémi Séba…).
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 13 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    url = df["SOURCEURL"].astype(str).str.lower()
    a1  = df["Actor1Name"].astype(str).str.upper()
 
    url_keywords = [
        "talon", "wadagni", "kemi-seba", "kemi%seba",
        "tigri", "boko", "homeky", "azannai",
        "soglo", "hounsou", "vlavonou", "seidou",
    ]
    actor_keywords = ["TALON", "WADAGNI", "SOGLO", "SEIDOU", "LAFIA", "ZOSSOU"]
 
    # Pour les patterns avec %, on fait un OR de contains individuels
    mask_url = url.str.contains(
        "|".join(k.replace("%", ".*") for k in url_keywords), na=False, regex=True
    )
    mask_actor = a1.str.contains("|".join(actor_keywords), na=False)
 
    df = df[mask_url | mask_actor]
    df = _base_transform(df)
    df = df.sort_values("NumArticles", ascending=False).head(3_000).reset_index(drop=True)
    return df
 
 
def compute_personnalites_etrangeres(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Personnalités étrangères influençant le Bénin (Tinubu, Macron…).
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 14 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    url = df["SOURCEURL"].astype(str).str.lower()
    a1  = df["Actor1Name"].astype(str).str.upper()
    a2  = df["Actor2Name"].astype(str).str.upper()
 
    url_keywords    = ["tinubu", "macron", "traore", "ouattara", "bazoum", "tchiani"]
    actor_keywords  = ["MACRON", "TINUBU"]
 
    mask_url    = url.str.contains("|".join(url_keywords), na=False)
    mask_actors = (
        a1.str.contains("|".join(actor_keywords), na=False) |
        a2.str.contains("|".join(actor_keywords), na=False)
    )
 
    df = df[mask_url | mask_actors]
    df = _base_transform(df)
    df = df.sort_values("NumArticles", ascending=False).head(2_000).reset_index(drop=True)
    return df
 
 
def compute_liberte_presse(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Liberté de presse et répression civile.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 15 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    df["EventRootCode"] = df["EventRootCode"].astype(str).str.zfill(2)
    df = df[df["EventRootCode"].isin(["15", "16", "17", "18"])]
 
    a2  = df["Actor2Name"].astype(str).str.upper()
    url = df["SOURCEURL"].astype(str).str.lower()
 
    actor2_keywords = ["JOURNALIST", "ACTIVIST", "OPPOSITION", "DEMOCRATIC"]
    source_keywords = ["rsf", "ifex", "amnesty", "hrw", "constitution", "mandat"]
 
    mask_actors  = a2.str.contains("|".join(actor2_keywords), na=False)
    mask_sources = url.str.contains("|".join(source_keywords), na=False)
 
    df = df[mask_actors | mask_sources]
    df = _base_transform(df)
    df = df.sort_values("AvgTone", ascending=True).head(2_000).reset_index(drop=True)
    return df

def compute_can2025_sport(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    CAN 2025 — Bénin sur la scène sportive internationale.
    Couvre les matchs, résultats, couverture médiatique internationale
    du football béninois.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 16 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    a1  = df["Actor1CountryCode"].astype(str)
    a2  = df["Actor2CountryCode"].astype(str)
    url = df["SOURCEURL"].astype(str).str.lower()
 
    # Égypte vs Bénin (match CAN 2025) + mots-clés URL
    mask_egypt  = (a1 == "EGY") | (a2 == "EGY")
    mask_url    = url.str.contains(
        "afcon|africa-cup|coppa-dafrica|afrika-cup|coupe-afrique|can-2025|can2025",
        na=False
    )
 
    df = df[mask_egypt | mask_url]
    df = _base_transform(df)
    df = df.sort_values("NumArticles", ascending=False).head(2_000).reset_index(drop=True)
    return df
 
 
def compute_economie_developpement(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Économie, finances et développement du Bénin.
    Sources : Bloomberg, Reuters, Ecofinagency, FMI, Banque mondiale, BAD.
    Couvre : énergie solaire, agriculture, finance, infrastructure,
             plateforme de réclamations, formation agricole.
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 17 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    url = df["SOURCEURL"].astype(str).str.lower()
 
    source_keywords = [
        "ecofinagency",
        "bloomberg",
        "reuters",
        "imf.org",
        "worldbank",
        "afdb.org",
        "banquemondiale",
        "unctad",
    ]
 
    mask_url = url.str.contains("|".join(source_keywords), na=False)
    df = df[mask_url]
    df = _base_transform(df)
    df = df.sort_values("date", ascending=False).head(2_000).reset_index(drop=True)
    return df
 
def compute_sources_officielles(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Sources officielles — ECOWAS + gouvernement béninois.
    Ce que les institutions disent officiellement du Bénin
    vs ce que le monde dit du Bénin.
    Couvre : ecowas.int, gouv.bj, presidence.bj
    Source : gdelt_benin_raw (DATA_RAW_PATH).
    Miroir exact de la REQUÊTE 18 (queries.sql).
    """
    df = _filter_year(df_raw)
 
    url = df["SOURCEURL"].astype(str).str.lower()
 
    source_keywords = [
        "ecowas.int",
        "gouv.bj",
        "presidence.bj",
    ]
 
    mask_url = url.str.contains("|".join(source_keywords), na=False)
    df = df[mask_url]
    df = _base_transform(df)
    df = df.sort_values("date", ascending=False).head(2_000).reset_index(drop=True)
    return df

def compute_medias_beninois(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Ce que la presse béninoise dit du Bénin.
    Vision interne — narrative locale.
    """
    df = _filter_year(df_raw)

    BENINOIS_DOMAINS = [
        'gouv.bj',
        'lanouvelletribune.info',
        '24haubenin.info',
        'promptnewsonline.com',
        'beninactu.net',
        'matinlibre.com',
        'fraternite.info',
        'acotonou.com',
        'beninwebtv.com',
        'quotidienlematinal.com',
        'benin-adpao.bj',
        'presidence.bj',
    ]

    pattern = '|'.join(BENINOIS_DOMAINS)
    url = df['SOURCEURL'].astype(str).str.lower()
    df = df[url.str.contains(pattern, na=False)]
    df = _base_transform(df)
    df = df.sort_values('date', ascending=False).head(3_000).reset_index(drop=True)
    return df


def compute_medias_internationaux(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Ce que la presse internationale dit du Bénin.
    Vision externe — narrative mondiale.
    """
    df = _filter_year(df_raw)

    # Exclure les médias béninois ET le bruit nigérian
    BENINOIS_DOMAINS = [
        'gouv.bj', 'lanouvelletribune.info', '24haubenin.info',
        'promptnewsonline.com', 'beninactu.net', 'matinlibre.com',
        'presidence.bj', 'fraternite.info', 'acotonou.com',
    ]
    NIGERIAN_DOMAINS = [
        'punchng.com', 'dailypost.ng', 'premiumtimesng.com',
        'vanguardngr.com', 'thenationonlineng.net', 'channelstv.com',
        'thisdaylive.com', 'nigerianobservernews.com', 'guardian.ng',
        'thesun.ng', 'leadership.ng', 'legit.ng', 'dailytrust.com',
    ]

    pattern_exclude = '|'.join(BENINOIS_DOMAINS + NIGERIAN_DOMAINS)
    url = df['SOURCEURL'].astype(str).str.lower()
    df = df[~url.str.contains(pattern_exclude, na=False)]
    df = _base_transform(df)
    df = df.sort_values('NumArticles', ascending=False).head(5_000).reset_index(drop=True)
    return df



def transform_thematic(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """
    Transformation générique pour tous les datasets thématiques :
    zoom_dec2025, zoom_election2026, culture_tourisme,
    cooperation_ben_nga, securite_nord, femmes_benin,
    chine_benin, personnalites_benin, personnalites_etrangeres,
    liberte_presse.
    """
    df = parse_sqldate(df)
    df = normalize_event_code(df)
    df = clean_actors(df)
    df = flag_sentiment(df)
    df = drop_duplicates_strict(df, subset=[c for c in ["date", "Actor1Name", "EventRootCode", "SOURCEURL"] if c in df.columns])
    return df



# ---------------------------------------------------------------------------
# REGISTRE DES TRANSFORMATIONS
# Format : label → (input_path, output_path, transform_fn)
# ---------------------------------------------------------------------------

def build_registry() -> list[tuple]:
    """
    Retourne la liste ordonnée des transformations à appliquer.

    Règle fondamentale :
        - input_path  → toujours data/raw/       (source intacte, jamais écrasée)
        - output_path → toujours data/processed/ (résultat transformé)


    Cela garantit que le pipeline est idempotent : on peut le relancer
    autant de fois que nécessaire, même après avoir vidé data/processed/.
    """
    from config import (
        DATA_RAW_PATH,   DATA_CLEAN_PATH,
        DATA_RAW_GEO_PATH,    DATA_GEO_PATH,
        DATA_TONE_PATH,  DATA_ACTORS_PATH,  DATA_EVENTS_PATH,
        DATA_ZOOM_DEC2025_PATH,  DATA_ZOOM_ELECTION_PATH,
        DATA_CULTURE_PATH,       DATA_COOPERATION_NGA_PATH,
        DATA_SECURITE_NORD_PATH, DATA_FEMMES_PATH,
        DATA_CHINE_PATH,         DATA_PERSO_BENIN_PATH,
        DATA_PERSO_ETRANGERES_PATH, DATA_LIBERTE_PRESSE_PATH,
        DATA_CAN2025_PATH, DATA_ECONOMIE_PATH, DATA_SOURCES_OFF_PATH,
        DATA_MEDIAS_BENINOIS_PATH, DATA_MEDIAS_INTERNATIONAUX_PATH,
    )

    thematic_computes = [
        ("zoom_dec2025",             DATA_RAW_PATH, DATA_ZOOM_DEC2025_PATH,     compute_zoom_dec2025),
        ("zoom_election2026",        DATA_RAW_PATH, DATA_ZOOM_ELECTION_PATH,    compute_zoom_election2026),
        ("culture_tourisme",         DATA_RAW_PATH, DATA_CULTURE_PATH,          compute_culture_tourisme),
        ("cooperation_ben_nga",      DATA_RAW_PATH, DATA_COOPERATION_NGA_PATH,  compute_cooperation_ben_nga),
        ("securite_nord",            DATA_RAW_PATH, DATA_SECURITE_NORD_PATH,    compute_securite_nord_thematic),
        ("femmes_benin",             DATA_RAW_PATH, DATA_FEMMES_PATH,           compute_femmes_benin),
        ("chine_benin",              DATA_RAW_PATH, DATA_CHINE_PATH,            compute_chine_benin),
        ("personnalites_benin",      DATA_RAW_PATH, DATA_PERSO_BENIN_PATH,      compute_personnalites_benin),
        ("personnalites_etrangeres", DATA_RAW_PATH, DATA_PERSO_ETRANGERES_PATH, compute_personnalites_etrangeres),
        ("liberte_presse",           DATA_RAW_PATH, DATA_LIBERTE_PRESSE_PATH,   compute_liberte_presse),
        ("can2025_sport",            DATA_RAW_PATH, DATA_CAN2025_PATH,          compute_can2025_sport),
        ("economie",                 DATA_RAW_PATH, DATA_ECONOMIE_PATH,         compute_economie_developpement),
        ("sources_officielles",      DATA_RAW_PATH, DATA_SOURCES_OFF_PATH,      compute_sources_officielles),
        ("medias_beninois",          DATA_RAW_PATH, DATA_MEDIAS_BENINOIS_PATH,  compute_medias_beninois),
        ("medias_internationaux",    DATA_RAW_PATH, DATA_MEDIAS_INTERNATIONAUX_PATH, compute_medias_internationaux),
    ]
    
    registry = [
        ("gdelt_benin_main",  DATA_RAW_PATH,     DATA_CLEAN_PATH,   transform_main),
        ("geo_events",        DATA_RAW_GEO_PATH, DATA_GEO_PATH,     transform_geo),
        ("tone_monthly",      DATA_CLEAN_PATH,   DATA_TONE_PATH,    _wrap_aggregate(compute_tone_monthly)),
        ("actors_country",    DATA_CLEAN_PATH,   DATA_ACTORS_PATH,  _wrap_aggregate(compute_actors_country)),
        ("events_by_type",    DATA_CLEAN_PATH,   DATA_EVENTS_PATH,  _wrap_aggregate(compute_events_by_type)),
    ]

    for entry in thematic_computes:
        registry.append(entry)
        
    return registry


def _wrap_aggregate(fn):
    """
    Wrapper pour les fonctions d'agrégat qui lisent gdelt_benin_clean.
    Permet de les utiliser dans le registre sans changer l'interface run().
    """
    def wrapped(df: pd.DataFrame) -> pd.DataFrame:
        return fn(df)
    wrapped.__name__ = fn.__name__
    return wrapped


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------

def run() -> int:
    """
    Applique toutes les transformations du registre.

    Returns:
        0 si toutes les transformations réussissent, 1 sinon.
    """
    logger.info("=" * 60)
    logger.info("GDELT Bénin — Pipeline de transformation")
    logger.info("=" * 60)

    registry = build_registry()
    results  = {"success": [], "failed": []}

    for entry in registry:
        # Les datasets thématiques passent transform_thematic avec le label
        if len(entry) == 4:
            label, input_path, output_path, fn = entry
        else:
            raise ValueError(f"Entrée de registre invalide : {entry}")

        df = load(input_path, label)
        if df is None:
            results["failed"].append(label)
            continue

        # SKIP pour les agrégats si BigQuery les a déjà produits dans output_path
        # Détecté par : input_path == output_path de gdelt_benin_clean ET output existe déjà
        is_aggregate = fn.__name__ in ("compute_tone_monthly", "compute_actors_country", "compute_events_by_type")
        if is_aggregate and Path(str(output_path)).exists():
            logger.info(f"[{label}] Agrégat déjà présent (BigQuery mode) → recalcul ignoré.")
            results["success"].append(label)
            continue

        try:
            # transform_thematic attend un label en second argument
            if fn is transform_thematic:
                df_out = fn(df, label)
            else:
                df_out = fn(df)

            save(df_out, output_path, label)
            results["success"].append(label)

        except Exception as e:
            logger.error(f"[{label}] Erreur transformation : {e}")
            results["failed"].append(label)

    # Rapport final
    total = len(registry)
    nb_ok = len(results["success"])
    nb_ko = len(results["failed"])

    logger.info("=" * 60)
    logger.info(f"Transformation terminée — {nb_ok}/{total} réussies")
    if results["failed"]:
        logger.warning(f"Échecs ({nb_ko}) : {results['failed']}")
    logger.info("=" * 60)

    return 0 if not results["failed"] else 1