import json
from pathlib import Path

from language_model import get_relevance, iter_metawiki_entries


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_relevance_fallback_is_non_empty_for_every_seed_entry():
    data = json.loads((PROJECT_ROOT / "wikistub_seed.json").read_text(encoding="utf-8"))
    entries = [entry for _, _, entry in iter_metawiki_entries(data)]

    assert len(entries) == 630
    assert all(get_relevance(entry, "en") for entry in entries)


def test_explicit_english_relevance_wins_and_unknown_language_falls_back_to_german():
    entry = {
        "relevance": "Deutsche Relevanz.",
        "relevance_i18n": {
            "de": "Deutsche Relevanz.",
            "en": "English relevance.",
        },
    }

    assert get_relevance(entry, "en") == "English relevance."
    assert get_relevance(entry, "fr") == "Deutsche Relevanz."


def test_embedding_search_spec_covers_local_contract_and_fallback():
    spec = (PROJECT_ROOT / "EMBEDDING_SEARCH_API.md").read_text(encoding="utf-8")

    for marker in (
        "wikistub-local-search-v1",
        "127.0.0.1",
        "GET /v1/health",
        "GET /v1/capabilities",
        "POST /v1/search",
        "POST /v1/index/rebuild",
        "embedding_backend_unavailable",
        "source_sha256",
        "relevance_i18n",
    ):
        assert marker in spec
