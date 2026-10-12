#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
translate.py - Optionale KI-Übersetzung für WikiStub-Seed
=======================================================

Übersetzt deutsche Wissens-Stubs ins Englische via Claude API.

Voraussetzungen:
    pip install anthropic
    Configure the ANTHROPIC_API_KEY environment variable before an API run.

Nutzung als Modul:
    from translate import translate_text
    english = translate_text(
        "Kurzdefinition auf Deutsch", max_budget_usd=0.01
    )

Ohne API-Key oder ohne installiertes Paket wird "" zurückgegeben (kein Fehler).
"""

import os
import math
import sys
import time

from language_model import SUPPORTED_LANGUAGES, normalize_language_code

MODEL_ID = "claude-haiku-4-5-20251001"
MAX_OUTPUT_TOKENS = 500
INPUT_USD_PER_MILLION_TOKENS = 1.0
OUTPUT_USD_PER_MILLION_TOKENS = 5.0
PRICING_AS_OF = "2026-07-15"
_MESSAGE_OVERHEAD_TOKENS = 256


def _translation_prompt(text: str, target_lang: str) -> str:
    lang_names = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
        "zh": "Chinese",
        "ja": "Japanese",
        "ru": "Russian",
    }
    target_lang = normalize_language_code(target_lang)
    if target_lang not in SUPPORTED_LANGUAGES or target_lang == "de":
        raise ValueError(
            "target_lang must be one of: "
            + ", ".join(lang for lang in SUPPORTED_LANGUAGES if lang != "de")
        )
    target_name = lang_names[target_lang]
    return (
        f"Translate the following German academic definition to {target_name}. "
        f"Return only the translation, no explanations or additional text.\n\n"
        f"German text: {text}"
    )


def estimate_max_request_cost_usd(text: str, target_lang: str = "en") -> float:
    """Return a conservative preflight ceiling for one standard API request.

    Pricing is pinned to Claude Haiku 4.5 standard API rates checked on
    2026-10-12. UTF-8 byte length plus protocol overhead bounds input tokens;
    output is bounded by ``MAX_OUTPUT_TOKENS``. This is a local estimate, not
    a provider-enforced spending limit or a guarantee of the billed amount.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    prompt = _translation_prompt(text, target_lang)
    max_input_tokens = len(prompt.encode("utf-8")) + _MESSAGE_OVERHEAD_TOKENS
    return (
        max_input_tokens * INPUT_USD_PER_MILLION_TOKENS / 1_000_000
        + MAX_OUTPUT_TOKENS * OUTPUT_USD_PER_MILLION_TOKENS / 1_000_000
    )


def estimate_batch_max_cost_usd(texts: list[str], target_lang: str = "en") -> float:
    return sum(estimate_max_request_cost_usd(text, target_lang) for text in texts)


def validate_max_budget_usd(max_budget_usd: float | None) -> float:
    """Return a valid explicit positive ceiling or reject it before an API call."""
    if not isinstance(max_budget_usd, (int, float)) or isinstance(max_budget_usd, bool):
        raise ValueError("max_budget_usd must be a finite positive explicit cost ceiling")
    try:
        budget = float(max_budget_usd)
    except (OverflowError, ValueError):
        raise ValueError(
            "max_budget_usd must be a finite positive explicit cost ceiling"
        ) from None
    if not math.isfinite(budget) or budget <= 0:
        raise ValueError("max_budget_usd must be a finite positive explicit cost ceiling")
    return budget


def _validate_estimate_within_budget(projected_cost: float, max_budget_usd: float) -> None:
    if projected_cost > max_budget_usd:
        raise ValueError(
            f"projected maximum cost ${projected_cost:.6f} exceeds "
            f"budget ${max_budget_usd:.6f}"
        )


def translate_text(
    text: str,
    target_lang: str = "en",
    *,
    max_budget_usd: float | None = None,
) -> str:
    """
    Übersetzt Text via Claude API.

    Args:
        text:        Zu übersetzender Text (Deutsch)
        target_lang: Zielsprache als ISO-Code (default: "en")

    Returns:
        Übersetzter Text oder "" falls API nicht verfügbar.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    target_lang = normalize_language_code(target_lang)
    _translation_prompt(text, target_lang)
    if not text.strip():
        return ""

    try:
        import anthropic
    except ImportError:
        return ""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    budget = validate_max_budget_usd(max_budget_usd)
    projected_cost = estimate_max_request_cost_usd(text, target_lang)
    _validate_estimate_within_budget(projected_cost, budget)
    prompt = _translation_prompt(text, target_lang)

    try:
        client = anthropic.Anthropic(api_key=api_key, max_retries=0)
        message = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_OUTPUT_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as exc:
        print(f"Translation error ({type(exc).__name__}).", file=sys.stderr)
        return ""


def is_available() -> bool:
    """Prüft ob die Translation-API verfügbar ist."""
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def translate_batch(
    texts: list[str],
    target_lang: str = "en",
    delay: float = 0.3,
    *,
    max_budget_usd: float | None = None,
) -> list[str]:
    """
    Übersetzt eine Liste von Texten mit optionalem Delay zwischen Anfragen.

    Args:
        texts:       Liste von Texten
        target_lang: Zielsprache als ISO-Code
        delay:       Wartezeit in Sekunden zwischen API-Anfragen (Rate-Limit)
        max_budget_usd: ausdrückliches Budget für die lokale Schätzung

    Returns:
        Liste von übersetzten Texten (gleiche Länge wie Input)
    """
    budget = validate_max_budget_usd(max_budget_usd)
    projected_cost = estimate_batch_max_cost_usd(texts, target_lang)
    _validate_estimate_within_budget(projected_cost, budget)
    if (
        not isinstance(delay, (int, float))
        or isinstance(delay, bool)
        or not math.isfinite(delay)
        or delay < 0
    ):
        raise ValueError("delay must be a finite non-negative number")

    results = []
    for i, text in enumerate(texts):
        result = translate_text(text, target_lang, max_budget_usd=budget)
        results.append(result)
        if result and delay > 0 and i < len(texts) - 1:
            time.sleep(delay)
    return results


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="WikiStub-Seed: Text-Übersetzung")
    parser.add_argument("text", nargs="?", help="Zu übersetzender Text")
    parser.add_argument(
        "--lang",
        default="en",
        choices=[lang for lang in SUPPORTED_LANGUAGES if lang != "de"],
        help="Zielsprache (default: en)",
    )
    parser.add_argument("--check", action="store_true", help="API-Verfügbarkeit prüfen")
    parser.add_argument(
        "--max-budget-usd",
        type=float,
        help="Freigegebenes lokales Schätzbudget in USD",
    )
    parser.add_argument(
        "--confirm-api-cost",
        action="store_true",
        help="Mögliche API-Kosten bestätigen",
    )
    args = parser.parse_args(argv)

    if args.check:
        if is_available():
            print("  Übersetzung verfügbar (ANTHROPIC_API_KEY gesetzt)")
        else:
            print("  Übersetzung nicht verfügbar.")
            print("  Bitte setze ANTHROPIC_API_KEY und installiere: pip install anthropic")
        return 0

    if not args.text:
        parser.print_help()
        return 1

    projected_cost = estimate_max_request_cost_usd(args.text, args.lang)
    if not args.confirm_api_cost:
        print("FEHLER: --confirm-api-cost muss gesetzt sein.")
        return 1
    try:
        budget = validate_max_budget_usd(args.max_budget_usd)
        _validate_estimate_within_budget(projected_cost, budget)
    except ValueError as exc:
        print(f"FEHLER: {exc}")
        return 1

    if not is_available():
        print("FEHLER: ANTHROPIC_API_KEY nicht gesetzt oder 'anthropic' nicht installiert.")
        return 1

    print(
        f"Lokale Kostenabschätzung: ${projected_cost:.6f}; "
        "dies ist kein providerseitiges Ausgabenlimit."
    )
    result = translate_text(args.text, args.lang, max_budget_usd=budget)
    if result:
        print(result)
        return 0

    print("FEHLER: Übersetzung fehlgeschlagen.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
