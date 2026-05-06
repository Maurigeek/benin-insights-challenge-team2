from __future__ import annotations

from collections import Counter
import re

import pandas as pd

ACTOR_KEEP_NAMES = {
    "ECOWAS",
    "WORLD BANK",
    "AFRICAN UNION",
    "UNITED NATIONS",
    "WORLD HEALTH ORGANIZATION",
    "INTERNATIONAL ORGANIZATION FOR MIGRATION",
    "AFRICAN DEVELOPMENT BANK",
}

ACTOR_NOISE_NAMES = {
    "INCONNU",
    "UNKNOWN",
    "BEN",
    "BENIN",
    "BENINESE",
    "BENIN CITY",
    "AFRICA",
    "AFRICANS",
    "GOVERNMENT",
    "POLICE",
    "MILITARY",
    "ARMY",
    "NAVY",
    "AUTHORITIES",
    "COMMUNITY",
    "PRESIDENT",
    "GOVERNOR",
    "MINIST",
    "MINISTRY",
    "SECRETARIAT",
    "PRISONER",
    "INTELLECTUAL",
    "MAYOR",
    "BISHOP",
    "PRIEST",
    "UNIVERSITY",
    "MEDIA",
    "ACTOR",
    "STUDENT",
    "CITIZEN",
    "VOTER",
    "SCHOOL",
    "TERRORIST",
    "RESIDENTS",
    "VILLAGE",
    "BUSINESS",
    "CRIMINAL",
    "TOURIST",
    "JOURNALIST",
    "ACTIVIST",
    "ADMINISTRATION",
    "GOVERNANCE",
    "FRENCH",
    "BRITISH",
    "NIGERIAN",
    "EUROPEAN",
    "YORUBA",
    "COMPANY",
    "BANK",
    "HOSPITAL",
    "FARMER",
    "COMMANDER",
    "SPOKESMAN",
    "TELEVISION",
    "LAWYER",
    "PRISON",
    "NA",
    "N/A",
    "NONE",
    "NULL",
}


def _extract_location_tokens(dataframe: pd.DataFrame) -> set[str]:
    if "ActionGeo_FullName" not in dataframe.columns:
        return set()

    location_tokens: set[str] = set()
    for value in dataframe["ActionGeo_FullName"].dropna().astype(str):
        for token in re.split(r"[,;/|]+", value):
            cleaned = token.strip().upper()
            if cleaned:
                location_tokens.add(cleaned)
    return location_tokens


def _clean_actor_name(name: object, country_code: object, location_tokens: set[str]) -> str:
    text = re.sub(r"\s+", " ", str(name or "").strip())
    if not text or text.lower() == "nan":
        return ""

    upper_text = text.upper()
    upper_code = str(country_code or "").strip().upper()

    if upper_text in ACTOR_NOISE_NAMES:
        return ""
    if upper_text in location_tokens and upper_text not in ACTOR_KEEP_NAMES:
        return ""
    if len(text) < 3 or text.isdigit():
        return ""
    if upper_code not in {"", "NAN", "INCONNU"} and upper_text not in ACTOR_KEEP_NAMES:
        return ""

    return text.title() if text.isupper() else text


def extract_actor_counts(dataframe: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Build a cleaned actor ranking from structured GDELT actor fields."""
    if limit <= 0:
        raise ValueError("limit must be strictly positive.")

    location_tokens = _extract_location_tokens(dataframe)
    counter: Counter[str] = Counter()

    actor_columns = [
        ("Actor1Name", "Actor1CountryCode"),
        ("Actor2Name", "Actor2CountryCode"),
    ]

    for name_col, code_col in actor_columns:
        if name_col not in dataframe.columns:
            continue

        names = dataframe[name_col].fillna("").astype(str)
        if code_col in dataframe.columns:
            codes = dataframe[code_col].fillna("").astype(str)
        else:
            codes = pd.Series([""] * len(dataframe), index=dataframe.index)

        for actor_name, actor_code in zip(names, codes):
            cleaned = _clean_actor_name(actor_name, actor_code, location_tokens)
            if cleaned:
                counter[cleaned] += 1

    return pd.DataFrame(counter.most_common(limit), columns=["Acteur", "Nombre"])
