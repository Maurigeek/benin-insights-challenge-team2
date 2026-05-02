from __future__ import annotations

from collections.abc import Iterable
from typing import Any

try:
    import spacy
except ImportError as import_error:  # pragma: no cover
    raise ImportError(
        "spaCy is required. Install with: pip install spacy && python -m spacy download en_core_web_sm"
    ) from import_error

_NLP = spacy.load("en_core_web_sm")


def _deduplicate(items: Iterable[str]) -> list[str]:
    """Preserve order while removing duplicates."""
    return list(dict.fromkeys(item.strip() for item in items if item and item.strip()))


def _normalize_text(text: Any) -> str:
    """Normalize one input text while tolerating None values."""
    if text is None:
        return ""
    return str(text).strip()


def extract_entities(texts: list[str] | None) -> list[dict[str, list[str]]]:
    """Extract persons, organizations, and locations from a list of texts.

    Parameters
    ----------
    texts:
        List of input texts to process with spaCy NER. ``None`` returns an empty list.

    Returns
    -------
    list[dict[str, list[str]]]
        One dictionary per input text, with three keys:
        ``persons``, ``orgs``, and ``locations``.
    """
    if texts is None:
        return []
    if not isinstance(texts, list):
        raise TypeError("texts must be provided as a list of strings or None.")

    prepared_texts = [_normalize_text(text) for text in texts]
    results: list[dict[str, list[str]]] = []

    for doc in _NLP.pipe(prepared_texts):
        persons = _deduplicate(ent.text for ent in doc.ents if ent.label_ == "PERSON")
        orgs = _deduplicate(ent.text for ent in doc.ents if ent.label_ == "ORG")
        locations = _deduplicate(
            ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC"}
        )

        results.append(
            {
                "persons": persons,
                "orgs": orgs,
                "locations": locations,
            }
        )

    return results
