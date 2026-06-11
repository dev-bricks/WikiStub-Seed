"""Shared language model helpers for MetaWiki data."""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping, MutableMapping


SUPPORTED_LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"]
REQUIRED_LANGUAGES = ["de", "en"]
DEFAULT_LANGUAGE = "de"
FALLBACK_LANGUAGES = ["de", "en"]

LEGACY_DEFINITION_FIELDS = {"de": "definition_de", "en": "definition_en"}
LEGACY_RELEVANCE_FIELD = "relevance"
LOCALIZED_RELEVANCE_FIELD = "relevance_i18n"


def normalize_language_code(value: object) -> str:
    """Return the base lowercase language code or an empty string."""
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("_", "-").split("-")[0]


def _clean_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def normalize_localized_map(
    value: object = None,
    legacy: Mapping[str, object] | None = None,
    *,
    overwrite_legacy: bool = False,
) -> dict[str, str]:
    """Normalize a language keyed text map to all supported language slots."""
    result = {lang: "" for lang in SUPPORTED_LANGUAGES}

    if isinstance(value, Mapping):
        for raw_lang, raw_text in value.items():
            lang = normalize_language_code(raw_lang)
            if lang in result:
                result[lang] = _clean_text(raw_text)

    if legacy:
        for raw_lang, raw_text in legacy.items():
            lang = normalize_language_code(raw_lang)
            if lang in result and (overwrite_legacy or not result[lang]):
                result[lang] = _clean_text(raw_text)

    return result


def definition_legacy(entry: Mapping[str, object]) -> dict[str, object]:
    return {
        lang: entry.get(field, "")
        for lang, field in LEGACY_DEFINITION_FIELDS.items()
    }


def relevance_legacy(entry: Mapping[str, object]) -> dict[str, object]:
    relevance = entry.get(LEGACY_RELEVANCE_FIELD, "")
    return {DEFAULT_LANGUAGE: relevance if isinstance(relevance, str) else ""}


def localized_text(
    value: object,
    lang: str = DEFAULT_LANGUAGE,
    *,
    legacy: Mapping[str, object] | None = None,
) -> str:
    """Return text for lang with the project fallback chain."""
    normalized = normalize_localized_map(value, legacy)
    candidates = [normalize_language_code(lang), *FALLBACK_LANGUAGES]

    for candidate in candidates:
        if candidate and normalized.get(candidate):
            return normalized[candidate]

    return next((text for text in normalized.values() if text), "")


def get_definition(entry: Mapping[str, object], lang: str = DEFAULT_LANGUAGE) -> str:
    return localized_text(entry.get("definitions"), lang, legacy=definition_legacy(entry))


def get_relevance(entry: Mapping[str, object], lang: str = DEFAULT_LANGUAGE) -> str:
    relevance_value = entry.get(LOCALIZED_RELEVANCE_FIELD)
    if relevance_value is None and isinstance(entry.get(LEGACY_RELEVANCE_FIELD), Mapping):
        relevance_value = entry.get(LEGACY_RELEVANCE_FIELD)
    return localized_text(relevance_value, lang, legacy=relevance_legacy(entry))


def normalize_entry(entry: Mapping[str, object]) -> dict[str, object]:
    """Return a backwards-compatible entry with canonical localized fields."""
    normalized: dict[str, object] = dict(entry)
    definitions = normalize_localized_map(
        entry.get("definitions"),
        definition_legacy(entry),
    )

    relevance_source = entry.get(LOCALIZED_RELEVANCE_FIELD)
    if relevance_source is None and isinstance(entry.get(LEGACY_RELEVANCE_FIELD), Mapping):
        relevance_source = entry.get(LEGACY_RELEVANCE_FIELD)
    relevance_i18n = normalize_localized_map(relevance_source, relevance_legacy(entry))

    normalized["definitions"] = definitions
    normalized["definition_de"] = definitions["de"]
    normalized["definition_en"] = definitions["en"]
    normalized[LOCALIZED_RELEVANCE_FIELD] = relevance_i18n
    normalized[LEGACY_RELEVANCE_FIELD] = relevance_i18n["de"]
    return normalized


def iter_metawiki_entries(data: Mapping[str, object]):
    root = data.get("MetaWiki")
    if not isinstance(root, Mapping):
        return

    for category, subcategories in root.items():
        if not isinstance(subcategories, Mapping):
            continue
        for subcategory, entries in subcategories.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, Mapping):
                    yield category, subcategory, entry


def normalize_metawiki_data(data: Mapping[str, object]) -> dict[str, object]:
    """Deep-copy MetaWiki data and add canonical language maps to every stub."""
    normalized = deepcopy(data)
    root = normalized.get("MetaWiki")
    if not isinstance(root, MutableMapping):
        return normalized

    for _, _, entry in iter_metawiki_entries(normalized):
        original = dict(entry)
        entry.clear()
        entry.update(normalize_entry(original))

    return normalized


def language_model_metadata() -> dict[str, object]:
    return {
        "version": 1,
        "default_language": DEFAULT_LANGUAGE,
        "languages": list(SUPPORTED_LANGUAGES),
        "required_languages": list(REQUIRED_LANGUAGES),
        "fallback_chain": list(FALLBACK_LANGUAGES),
        "canonical_fields": {
            "definitions": "definitions.{lang}",
            "relevance": f"{LOCALIZED_RELEVANCE_FIELD}.{{lang}}",
        },
        "legacy_fields": {
            "definition_de": "definitions.de",
            "definition_en": "definitions.en",
            "relevance": f"{LOCALIZED_RELEVANCE_FIELD}.de",
        },
    }
