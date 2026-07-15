"""Explicit dataset exceptions that remain visible to validation gates."""

from __future__ import annotations

from collections.abc import Iterable

from language_model import identifier_key


_ALLOWED_DUPLICATE_LOCATIONS = {
    identifier_key("Graphentheorie"): frozenset(
        {
            (
                identifier_key("07_Informatik_KI"),
                identifier_key("Theoretische_Informatik"),
            ),
            (identifier_key("01_Mathematik"), identifier_key("Diskrete_Mathematik")),
        }
    ),
    identifier_key("Metalle"): frozenset(
        {
            (identifier_key("03_Chemie"), identifier_key("Anorganische_Chemie")),
            (
                identifier_key("08_Technik_Ingenieurwesen"),
                identifier_key("Materialwissenschaft_Werkstofftechnik"),
            ),
        }
    ),
}


def duplicate_locations_are_allowed(
    title: object, locations: Iterable[tuple[object, object]]
) -> bool:
    """Return true only for an exact, reviewed cross-domain duplicate set."""
    normalized = frozenset(
        (identifier_key(category), identifier_key(subcategory))
        for category, subcategory in locations
    )
    return normalized == _ALLOWED_DUPLICATE_LOCATIONS.get(identifier_key(title))
