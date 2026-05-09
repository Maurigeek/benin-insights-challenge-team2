"""Label building for media impact prediction."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import pandas as pd

from src.models import config


def extract_source_domain(url: object) -> str:
    """Extract a normalized domain from a URL-like value."""
    if url is None:
        return ""
    text = str(url).strip()
    if not text:
        return ""

    parsed = urlparse(text)
    domain = parsed.netloc or parsed.path
    domain = domain.lower().lstrip("www.")
    return domain.split("/")[0]


def build_domain_set(dataframe: pd.DataFrame, source_column: str = config.MEDIA_SOURCE_COLUMN) -> set[str]:
    """Build a set of domains from a dataframe column of URLs."""
    if source_column not in dataframe.columns:
        raise ValueError(f"Missing required source column: {source_column}.")

    domains = {
        extract_source_domain(value)
        for value in dataframe[source_column].dropna().astype(str)
    }
    return {domain for domain in domains if domain}


def load_media_domains(
    benin_path: str | Path = config.MEDIA_BENIN_SOURCES_PATH,
    international_path: str | Path = config.MEDIA_INTERNATIONAL_SOURCES_PATH,
    source_column: str = config.MEDIA_SOURCE_COLUMN,
) -> tuple[set[str], set[str]]:
    """Load Benin and international media domains from processed data files."""
    root_dir = Path(__file__).resolve().parents[3]

    benin_path = Path(benin_path)
    if not benin_path.exists():
        benin_path = root_dir / benin_path

    international_path = Path(international_path)
    if not international_path.exists():
        international_path = root_dir / international_path

    benin_df = pd.read_csv(benin_path)
    international_df = pd.read_csv(international_path)
    return (
        build_domain_set(benin_df, source_column=source_column),
        build_domain_set(international_df, source_column=source_column),
    )


def build_media_label(
    dataframe: pd.DataFrame,
    benin_domains: Iterable[str],
    international_domains: Iterable[str],
    source_column: str = config.MEDIA_SOURCE_COLUMN,
) -> pd.Series:
    """Build a stable label for international media coverage.

    Returns a pandas Series with values:
    - 1 for international sources
    - 0 for Benin sources
    - <NA> for unknown sources
    """
    if source_column not in dataframe.columns:
        raise ValueError(f"Missing required source column: {source_column}.")

    benin_set = {domain.lower() for domain in benin_domains}
    international_set = {domain.lower() for domain in international_domains}

    domains = dataframe[source_column].apply(extract_source_domain)
    labels = pd.Series(pd.NA, index=dataframe.index, dtype="Int64")
    labels.loc[domains.isin(international_set)] = 1
    labels.loc[domains.isin(benin_set)] = 0
    return labels
